from functools import wraps
from CoverLetterGeniusWebSite.settings import JWT_AUTH
import jwt
from clApp.src.cookies_handler import *
from django.shortcuts import render, redirect
from jwt.algorithms import RSAAlgorithm


""" all the jwt functions should be able to work with both cognito access_token and id_token """


def token_required(func):
    """
    Decorator that checks if the user has a valid JWT token.
    We use the cognito access_token to authenticate the user when calling apis.
    :return: return the cognito sub value that is used as user's id in django db
    """

    @wraps(func)
    def decorated(request, *args, **kwargs):
        try:
            access_token = get_cookie(request, "access_token")
            cognito_sub = jwt_authenticate(access_token)['sub']
            kwargs['cognito_sub'] = cognito_sub # pass the cognito sub value to the decorated view
            request.cognito_sub = cognito_sub
        except Exception:
            return redirect('/signin')
        return func(request, *args, **kwargs)
    return decorated



def jwt_authenticate(jwt_token):
    """
    works with both cognito access and id token
    This function takes a JWT token and attempts to decode it using the specified parameters in JWT_AUTH.
    If the token is valid, it returns the decoded token. If the token is invalid, it prints an error message.
    """

    try:
        # Get the key ID from the JWT token header
        unverified_header = jwt.get_unverified_header(jwt_token)
        kid = unverified_header['kid']
        # pick a proper public key according to `kid` from token header
        public_key = RSAAlgorithm.from_jwk(JWT_AUTH["JWT_PUBLIC_KEY"][kid])

        return jwt.decode(jwt_token, public_key, algorithms=JWT_AUTH['JWT_ALGORITHM'],
                                   audience=JWT_AUTH['JWT_AUDIENCE'], issuer=JWT_AUTH['JWT_ISSUER'])

    except jwt.exceptions.InvalidTokenError as e:
        # Token is invalid
        print(f"Invalid token: {e}")
    except jwt.exceptions.ExpiredSignatureError as e:
        # Token is expired
        print(f"Expired token: {e}")
    except Exception as ex:
        # Handle any other exceptions
        print(f"Unexpected exception occurred: {ex}")



