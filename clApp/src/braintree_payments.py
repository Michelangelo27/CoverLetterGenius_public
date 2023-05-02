import braintree
from CoverLetterGeniusWebSite import settings
from functools import wraps
from clApp.models import User
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def subscription_required(func):
    """
    Decorator that checks if the user has an active subscription.
    """

    @wraps(func)
    def decorated(request, *args, **kwargs):
        try:
            if not hasattr(request, 'cognito_sub'):
                return redirect('/signin')

            user = User.objects.get(username=request.cognito_sub)
            if not user.subscription:
                return redirect('/payments')

        except Exception as ex:
            return redirect('/signin')

        return func(request, *args, **kwargs)
    return decorated



def get_gateway():
    return braintree.BraintreeGateway(
        braintree.Configuration(
            environment=braintree.Environment.Sandbox,
            merchant_id=settings.BRAINTREE_MERCHANT_ID,
            public_key=settings.BRAINTREE_PUBLIC_KEY,
            private_key=settings.BRAINTREE_PRIVATE_KEY
        )
    )

def user_exists(gateway, user):
    try:
        braintree_user = gateway.customer.find(user.username)
        if user.subscription_id is None:
            if hasattr(braintree_user.payment_methods[0], 'subscriptions'):
                # braintree_user.payment_methods[0].subscriptions[0].id c'è anche il plan_id nel caso si facciano più abbonamenti
                subscriptions = braintree_user.payment_methods[0].subscriptions
                if len(subscriptions) > 0:
                    user.subscription_id = subscriptions[0].id # Assuming only one subscription per customer
                    user.save
        return True
    except braintree.exceptions.not_found_error.NotFoundError:
        return False


def check_subscription_status(gateway, plan_id):
    try:
        subscription = gateway.subscription.find(plan_id)
        return subscription.status in ['Active', 'Past Due', 'Pending']
    except braintree.exceptions.not_found_error.NotFoundError:
        return False



def process_payment(gateway, payment_nonce, cognito_sub, email, user_exist, check_subscription):

    # if the user don't exist in braintree
    if not user_exist:
        result = gateway.customer.create({
            'id': cognito_sub,
            'email': email,
            'payment_method_nonce': payment_nonce,
            'credit_card': {
                'options': {
                    'make_default': True
                    # 'fail_on_duplicate_payment_method': True

                }
            }
        })

    # verify the account doesn't already have an active/PastDue/Pending payment

    # The user already exist in braintree
    else:
        result = gateway.customer.update(
            customer_id=cognito_sub,
            params={
            "payment_method_nonce":payment_nonce,
            "credit_card":{
                'options': {
                    'make_default': True
                    # 'fail_on_duplicate_payment_method': True
                }
            }}
        )

    return result




# todo to activate in production, check if it works properly
@csrf_exempt # allows to receive post from outsite the project
def braintree_webhook(request):
    if request.method == 'POST':
        webhook_notification = get_gateway.webhook_notification.parse(
            request.body.decode('utf-8'),
            braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully
        )
        user_id = webhook_notification.subscription.id
        subscription_status = webhook_notification.subscription.status
        if subscription_status in ['Active', 'Past Due']:
            # Grant access to the service
            user = User.objects.filter(subscription=user_id).first()
            if user:
                # todo save the subscription status in db?
                #user.subscription_status = subscription_status
                user.subscription = True
                user.save()
            else:
                # todo teorically it's impossible that the user doesn't exist cause it's checked at each logIn if exist,
                # todo  if doesn't, it's created,  but could be usefull to consider this case in logs anyway
                # Handle case where subscription ID is not associated with a user
                pass

            return HttpResponse(status=200)
        else:
            # Do not grant access to the service for other statuses
            return HttpResponseBadRequest('Subscription is not active or past due')
    else:
        return HttpResponseBadRequest('Invalid request method')




