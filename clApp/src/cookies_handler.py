from django.http import HttpResponse
from CoverLetterGeniusWebSite.settings import SESSION_COOKIE_AGE
import time
from functools import wraps


def cookie_expires_time():
    # Set the cookie expiration time to 2 hours from now
    # use epoch time value, it works with all timezones
    return int(time.time() + SESSION_COOKIE_AGE)


def set_cookie(response, cookie_name, cokiee_value):
    """
    This function is used to store the jwt as cookie in the client computer

    :param request: takes the django view request parameter
    :param cokiee_value:  value of the cookie
    :return: return the jwt or an exception if not found
    :return:

    -httponly: ensures that the cookie cannot be accessed by JavaScript, which helps prevent against cross-site
     scripting (XSS) attacks
    -secure: ensures that the cookie is only sent over HTTPS
    -samesite: specifies the SameSite attribute of the cookie, which helps protect against cross-site request
     forgery (CSRF) attacks
    - max_age is used to define for how much the cookie last, on Explorer max_age doesn't work so it's a session cookie
    - todo manage expire field  to work on explorer ( do the same of max_age but takes a date_time object)
    """


    response.set_cookie(cookie_name, cokiee_value, httponly=True, secure=True, samesite='Lax',
                        max_age=SESSION_COOKIE_AGE, expires=cookie_expires_time())
    return response


def get_cookie(request, cookie_name:str):
    """
    This function is used to retrieve cookies in the client computer
    :param request:  takes the django view request parameter
    :param cookie_name:  name with the cookie is saved in the client is a string
    :return: return the cookie or None if cookies is not found
    """

    response = request.COOKIES.get(cookie_name)
    return response


def pass_cookie(cookie_name):
    def decorator(func):
        @wraps(func)
        def decorated(request, *args, **kwargs):
            cookie_value = request.COOKIES.get(cookie_name)
            kwargs[cookie_name] = cookie_value
            return func(request, *args, **kwargs)
        return decorated
    return decorator