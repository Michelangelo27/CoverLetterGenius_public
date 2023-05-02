from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField
from django.utils.translation import gettext_lazy as _

from clApp.models import User

"""The scope of the code snippet is to demonstrate how to customize the Django admin interface for a custom
 user model called User."""

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = '__all__'
        field_classes = {'username': UsernameField}


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """ The CustomUserAdmin class is used to define how the User model should be displayed in the admin interface"""

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', )}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'subscription', 'is_superuser', 'groups', 'user_permissions', )}
        ),
        (_('Important dates'), {'fields': ('created_at', 'updated_at', )}),
    )
    readonly_fields = ('created_at', 'updated_at', )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'email', 'password1', 'password2', ),
        }),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'is_staff', 'is_active', )
