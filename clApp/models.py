from django.db import models
import uuid
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator




class AbstractBaseModel(models.Model):
    """
    Base abstract model, that has `uuid` instead of `id` and includes `created_at`, `updated_at` fields.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)


    class Meta:
        abstract = True

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.uuid}>'


class User(PermissionsMixin, AbstractBaseUser, AbstractBaseModel):
    """
    Table contains cognito-users & django-users.
    PermissionsMixin leverage built-in django model permission's system
    (which allows to limit information for staff users via Groups).
    Note: Django-admin user and app user not split in different tables because of simplicity of development.
    Some libraries assume there is only one user model, and they can't work with both.
    For example to have a history log of changes for entities - to save which user made a change of object attribute,
    perhaps, auth-related libs, and some other.
    With current implementation we don't need to fork, adapt and maintain third party packages.
    They should work out of the box.
    The disadvantage is - cognito-users will have unused fields which always empty. Not critical.


    :param: username for cognito_user (no admin or staff) is the id generated by cognito for each user and is used as id
            for all data (such as custumer_id)

    """

    username_validator = UnicodeUsernameValidator()

    ### Common fields ###
    # For cognito-users username will contain `sub` claim from jwt token
    # (unique identifier (UUID) for the authenticated user).
    # For django-users it will contain username which will be used to log in into django-admin site
    username = models.CharField('Username', max_length=255, unique=True, validators=[username_validator], db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    subscription = models.BooleanField(default=False, db_index=True)
    subscription_id = models.CharField(max_length=255, unique=True, null=True, default=None) #is the subscription id created by braintree
    name = models.TextField(max_length=100, null=True, default=None)
    hard_skills = models.TextField(max_length=900, null=True, default=None)
    soft_skills = models.TextField(max_length=900, null=True, default=None)
    education = models.TextField(max_length=900, null=True, default=None)
    work_experience = models.CharField(max_length=900, null=True, default=None)
    hobbies = models.CharField(max_length=900, null=True, default=None)

    STATUS_CHOICES = (
        (-1, 'Not selected'),
        (0, 'Working'),
        (1, 'Studying'),
        (2, 'Unemployed'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=-1)

    ### Cognito-user related fields ###
    # some additional fields which will be filled-out only for users registered via Cognito


    ### Django-user related fields ###
    # password is inherited from AbstractBaseUser
    email = models.EmailField('Email address', blank=True)  # allow non-unique emails
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']  # used only on createsuperuser

    @property
    def is_django_user(self):
        return self.has_usable_password()


    # command to create superuser
    #python manage.py create_encrypted_superuser --username your_username --email your_email@example.com




