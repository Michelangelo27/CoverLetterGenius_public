import boto3
import os
from definitions import cognito_client_id, cognito_users_pool_id, cognito_region
from botocore.exceptions import ClientError

def sign_up(email, password):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    try:
        response = client.sign_up(ClientId=cognito_client_id, Username=email, Password=password,)
        return "200"
    except ClientError as ex:
        error_code = ex.response['Error']['Code']
        error_message = ex.response['Error']['Message']
        if error_code == 'UsernameExistsException':
            response = 'This email is already registered. Please use another email or signin.'
        elif error_code == 'InvalidPasswordException':
            response = 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.'
        else:
            response = f'An error occurred during the signup, please try again: {ex}'
        return response
    except Exception as ex:
        response = f'An error occurred during the signup, please try again: {ex}'
        return response



def sign_in(email, password):
    try:
        client = boto3.client('cognito-idp', region_name=cognito_region)
        response = client.initiate_auth(ClientId=cognito_client_id, AuthFlow='USER_PASSWORD_AUTH',
                                        AuthParameters={'USERNAME': email, 'PASSWORD': password})

        return response
    except client.exceptions.NotAuthorizedException as e:
        raise Exception('Invalid email or password')

    except client.exceptions.UserNotFoundException as e:
        raise Exception('User not found')

    except client.exceptions.UserNotConfirmedException as e:
        raise Exception('User not confirmed')

    except Exception as e:
        raise Exception(str(e))



def get_user_info(access_token):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    response = client.get_user(AccessToken=access_token)
    print(response)
    return response



def delete_user(access_token):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    response = client.delete_user(AccessToken=access_token)
    print(response)
    return response



def require_new_verification_code(email, password):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    response = client.admin_create_user(UserPoolId=cognito_users_pool_id, Username=email, TemporaryPassword=password)
    print(response)
    return response



def reset_password(email):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    response = client.forgot_password(ClientId=cognito_client_id, Username=email)
    print(response)
    return response



def confirm_reset_password(email, code, password):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    response = client.confirm_forgot_password(ClientId=cognito_client_id, Username=email, ConfirmationCode=code,
                                              Password=password)
    print(response)
    return response



# todo verify it works
def add_attributes(access_token, attributes):
    client = boto3.client('cognito-idp', region_name=cognito_region)
    response = client.update_user_attributes(AccessToken=access_token, UserAttributes=attributes)
    return response


