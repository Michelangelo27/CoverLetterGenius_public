"""CoverLetterGeniusWebSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import home
    2. Add a URL to urlpatterns:  path('', home.as_view(), name='home')
Including another URLconf
    1. Import the include function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clApp import views
from clApp.src.braintree_payments import braintree_webhook


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('home/', views.home, name='home'),
    path('createnewpw/', views.createNewPw, name='createNewPw'),
    path('payments/', views.payments, name='payments'),
    path('landingpage/', views.landing_page, name='landing_page'),
    path('yourinfo/', views.yourInfo, name='yourinfo'),
    path('braintree_webhook/', braintree_webhook, name='braintree_webhook'),
    path('subscription/', views.subscription, name='subscription'),
    path('update_payment_method/', views.update_payment_method, name='update_payment_method'),
]
