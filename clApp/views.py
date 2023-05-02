from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from clApp.src.cognito import *
from clApp.src.InputValidator import *
from CoverLetterGeniusWebSite import settings
from clApp.src.braintree_payments import get_gateway, check_subscription_status, subscription_required, user_exists, process_payment
from definitions import *
from clApp.models import User
from clApp.src.jwt_handler import *


def signup(request):

    try:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                response = sign_up(email=email, password=password)
                if response == "200":
                    messages.success(request, 'We sent you an email with a link to confirm the account activation')
                    return redirect('/signin')

                else:
                    messages.warning(request, response)
                    return render(request, 'clApp/signup.html', {'email': email})

            else:
                # Handle form errors
                #messages.warning(request, not_handled_error)
                return render(request, 'clApp/signup.html', {'email': form['email'].data, 'form': form})  # form is used to pass erorr messages to each field

        if request.method == 'GET':
            return render(request, 'clApp/signup.html')

    except:
        messages.warning(request, not_handled_error_message)
        return render(request, 'clApp/signup.html')



def signin(request):
    try:
        if request.method == 'POST':
            form = SigninForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                response = sign_in(email=email, password=password)

                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    user_sub = jwt_authenticate(response['AuthenticationResult']['AccessToken'])["sub"]
                    redirect_response = redirect('/home')
                    set_cookie(response=redirect_response, cookie_name="access_token", cokiee_value=response['AuthenticationResult']['AccessToken'])
                    if not User.objects.filter(username=user_sub).exists():
                        # if there is not a user object in django db create it
                        new_cognito_user = User(username=user_sub, is_active=True)
                        new_cognito_user.set_unusable_password()
                        new_cognito_user.save()
                        # set first access cookie
                        set_cookie(response=redirect_response, cookie_name="new_user",
                                   cokiee_value=True)
                        set_cookie(response=redirect_response, cookie_name="new_user_set_info",
                                   cokiee_value=True)

                    return redirect_response

            else:
                # Handle form errors
                return render(request, 'clApp/signin.html', {'form': form})

        if request.method == 'GET':
            return render(request, 'clApp/signin.html')

    except Exception as ex:
        messages.warning(request, f"We are sorry, but we can't sign you in! {ex}")
        # todo specify the error from cognito ???
        return render(request, 'clApp/signin.html')



@token_required
def home(request, cognito_sub):
    try:

        if request.method == 'POST':
            user = User.objects.get(username=cognito_sub)
            # if the user doesn't have an active subscription, then is sent to the payments page
            if not user.subscription:
                messages.warning(request, subscription_required_message)
                return redirect("/payments")

            form = WorkInfoForm(request.POST)
            try:
                if form.is_valid():
                    #gpt_result = generate_prompt(form=form, user=user) #todo uncomment
                    gpt_result = "APPOSTO" # todo delete
                    return render(request, 'clApp/home.html', {'form': form, 'gpt_result': gpt_result})

                else:
                     # form is not valid
                     return render(request, 'clApp/home.html', {'form': form})

            except Exception as ex:
                return render(request, 'clApp/home.html', {'form': form})

        if request.method == 'GET':
            # new users are redirect to payments page
            if get_cookie(request, "new_user_set_info") != "False" and get_cookie(request, "new_user_set_info") is not None:
                return redirect('/payments')

            return render(request, 'clApp/home.html')

    except Exception as ex:
        messages.warning(request, not_handled_error_message)
        # todo specify the error from cognito ???
        print(ex)
        return render(request, 'clApp/home.html')



@token_required
def yourInfo(request, cognito_sub):

    try:
        if request.method == 'POST':
            user = User.objects.get(username=cognito_sub)
            form = YourInfoForm(request.POST)

            if form.is_valid():
                try:
                    # Update the user object with the values from the your_info form
                    user.name = form.cleaned_data.get('name')
                    user.status = form.cleaned_data.get('status')
                    user.hard_skills = form.cleaned_data.get('hard_skills')
                    user.soft_skills = form.cleaned_data.get('soft_skills')
                    user.education = form.cleaned_data.get('education')
                    user.work_experience = form.cleaned_data.get('work_experience')
                    user.hobbies = form.cleaned_data.get('hobbies')

                    user.save()

                    messages.success(request, data_succesfully_updated_message)
                    return redirect("/yourinfo", {'form': form})
                except Exception as ex:
                    messages.warning(request, data_savings_error_message)
                    return redirect("/yourinfo", {'form': form})

            else:
                messages.warning(request, dirty_data_message)
                return redirect("/yourinfo", {'form': form})

        if request.method == 'GET':
            user = User.objects.get(username=cognito_sub)
            your_info_context = {
                'name': user.name,
                'status': user.status,
                'hard_skills': user.hard_skills,
                'soft_skills': user.soft_skills,
                'education': user.education,
                'work_experience': user.work_experience,
                'hobbies': user.hobbies
            }
            form = YourInfoForm(your_info_context)

            redirect_response = render(request, 'clApp/yourInfo.html', {'form': form})
            messages.success(request, your_info_effort_message)
            if get_cookie(request, 'new_user_set_info'):
                set_cookie(response=redirect_response, cookie_name="new_user_set_info",
                           cokiee_value=False)
            return redirect_response

    except Exception as ex:
        messages.warning(request, f"We are sorry, but something went wrong while savings your info")
        return redirect("/yourinfo")



@token_required
def payments(request, cognito_sub):

    try:
        # generating braintree gateway
        gateway = get_gateway()
        # generating the client token
        client_token = gateway.client_token.generate()
    except:
        messages.warning(request, not_handled_error_message)
        return redirect('/payments')

    if request.method == 'POST':

        # Get the payment nonce from the request
        payment_nonce = request.POST['payment_method_nonce']
        if not payment_nonce:
            messages.warning(request, not_handled_error_message)
            return render(request, 'clApp/payments.html', {'client_token': client_token})

        try:
            user_info = get_user_info(access_token=get_cookie(request, "access_token"))
            if len(user_info) == 0 or cognito_sub != user_info['UserAttributes'][0]["Value"]:
                messages.warning(request, not_handled_error_message)
                return redirect('/signin')

            user = User.objects.get(username=cognito_sub)
            user_exist_in_braintree = user_exists(gateway, user)
            if user_exist_in_braintree:
                check_subscription_status_in_braintree = check_subscription_status(gateway=gateway, plan_id=user.subscription_id)
            else:
                check_subscription_status_in_braintree = False

            if user_exist_in_braintree and check_subscription_status_in_braintree:
                # if the user exist in braintree and has an active/PastDue/Pending status
                if not user.subscription:
                    user.subscription = True
                    user.save()
                redirect_response = redirect('/home')
                set_cookie(response=redirect_response, cookie_name="new_user_set_info",
                               cokiee_value=False)
                return redirect_response


            result = process_payment(gateway=gateway, payment_nonce=payment_nonce, cognito_sub=cognito_sub,
                                     email=user_info['UserAttributes'][2]["Value"], user_exist=user_exist_in_braintree,
                                     check_subscription=check_subscription_status_in_braintree)

        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'clApp/payments.html', {'client_token': client_token})

        if not result.is_success:
            messages.error(request, "Payment failed. Please try again.")
            return render(request, 'clApp/payments.html', {'client_token': client_token})

        # create braintree subscription
        try:
            subscription_result = gateway.subscription.create({
                'payment_method_token': result.customer.payment_methods[0].token,
                'plan_id': settings.plan_id,
            })

            if not subscription_result.is_success:
                messages.error(request, 'Could not create subscription.')
                return render(request, 'clApp/payments.html', {'client_token': client_token})

            # subscription was created successfully
            user.subscription = True
            user.subscription_id = subscription_result["subscription"]["id"]
            user.save()

        except Exception as ex:
            messages.error(request, str(ex))
            return render(request, 'clApp/payments.html')

        # new user
        if request.COOKIES.get('new_user_set_info'):
            return redirect('/yourinfo')

        # old users
        return redirect('/home')

    if request.method == 'GET':
        return render(request, 'clApp/payments.html', {'client_token': client_token})



def landing_page(request):
    if request.method == 'GET':
        return render(request, 'clApp/landing_page.html')



def createNewPw(request):
    # todo avoid session variables
    try:
        if request.method == 'POST':
            form = ConfirmPwForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('password')
                email = form.cleaned_data.get('email')
                code = form.cleaned_data.get('code')
                response = confirm_reset_password(email=email, code=code, password=password)
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    request.session['reset_pw'] = False
                    request.session['cognito_response'] = response
                    messages.success(request, 'Password has been successfully updated!')
                    return redirect('/signin')
        return render(request, 'clApp/createNewPw.html')
    except:
        messages.warning(request,
                         "Something went wrong during the password reset, If you didn't receive the reset code by email, ask for another one!")
        return render(request, 'clApp/signin.html')



def resetPassword(request):
    # todo avoid session variables
    try:
        if request.method == 'POST':
            form = ResetPwForm(request.POST)
            if form.is_valid():
                request.session['reset_pw'] = True
                return redirect('/createNewPw')
        return render(request, 'clApp/signin.html')
    except:
        messages.warning(request, "Something went wrong during the password reset, if you don't rec!")
        return render(request, 'clApp/signin.html')



@token_required
def cancel_subscription(request, cognito_sub):
    # todo work in progress
    try:
        gateway = get_gateway()
        user = User.objects.get(username=cognito_sub)
        #check if the user has an active/past due/Pending subscription
        if check_subscription_status(user.plan_id):
            result = gateway.subscription.cancel(user.plan_id)
            if result.is_success:
                # Successfully canceled the subscription
                # Don't update status in db, let the webhooks/ authomatic job do that
                return True

            else:
                pass

    except:
        pass



@token_required
def subscription(request, cognito_sub):
    try:
        if request.method == 'POST':
            # todo wip
            pass

        if request.method == 'GET':
            return render(request, 'clApp/subscription.html')

    except:
        # todo handle exptions
        pass


@token_required
def update_payments_method(request, cognito_sub):
    try:
        if request.method == 'POST':
            # todo wip
            pass

        if request.method == 'GET':
            return render(request, 'clApp/subscription.html')

    except Exception as ex:
        messages.warning(request, ex)
        return redirect("/home")




