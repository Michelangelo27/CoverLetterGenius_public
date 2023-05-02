from django import forms
from django.core.exceptions import ValidationError
import re
import logging

logger = logging.getLogger(__name__)

# todo add check to verify if terms and condition as been checked and save value and pass it as attribute to cognito
class SignupForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        pattern = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not pattern.match(email):
            raise ValidationError("Invalid email format!")
        return email

    def clean_password(self):
        password = self.data.get("password")
        confirm_password = self.data.get("confirm_password")

        #logger.error(f"pw: {password} confirmpw: {confirm_password}")
        errors = []
        if password != confirm_password:
            errors.append("Passwords do not match!")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long!")
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least 1 number!")
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least 1 uppercase letter!")
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least 1 lowercase letter!")
        if errors:
            self.cleaned_data['password_errors'] = errors
            raise forms.ValidationError(errors)

        return password


class SigninForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        pattern = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not pattern.match(email):
            raise ValidationError("Invalid email format!")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        errors = []
        if password == "" or password is None:
            errors.append("Password is required!")
        if errors:
            raise forms.ValidationError(errors)
        return password

class ConfirmPwForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def newPwForm(self):
        password = self.data.get("password")
        confirm_password = self.data.get("confirm_password")

        logger.error(f"pw: {password} confirmpw: {confirm_password}")
        errors = []
        if password != confirm_password:
            errors.append("Passwords do not match!")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long!")
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least 1 number!")
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least 1 uppercase letter!")
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least 1 lowercase letter!")
        if errors:
            raise forms.ValidationError(errors)
        return password

class ResetPwForm(forms.Form):
    email = forms.EmailField()
    def clean_email(self):
        email = self.cleaned_data.get("email")
        pattern = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not pattern.match(email):
            raise ValidationError("Invalid email format!")
        return email


class YourInfoForm(forms.Form):
    name = forms.CharField(max_length=50, required=False)
    status = forms.ChoiceField(choices=[('0', 'Working'), ('1', 'Studying'), ('2', 'Unemployed')])
    hard_skills = forms.CharField(max_length=900, required=False)
    soft_skills = forms.CharField(max_length=900, required=False)
    education = forms.CharField(widget=forms.Textarea, max_length=900, required=False)
    work_experience = forms.CharField(widget=forms.Textarea, max_length=900, required=False)
    hobbies = forms.CharField(widget=forms.Textarea, max_length=900, required=False)

    # def clean(self):
    #     name = self.data.get("name")
    #     status = self.data.get("status")
    #     hard_skills = self.data.get("hardSkills")
    #     soft_skills = self.data.get("softSkills")
    #     education = self.data.get("education")
    #     workxperience = self.data.get("workExperience")

        # if name is None:
        #     self.add_error("name", "Name is required")
        # if status is None:
        #     self.add_error("status", "Status is required")
        # if hardSkills is None:
        #     self.add_error("hardSkills", "Hard Skills are required")
        # if softSkills is None:
        #     self.add_error("softSkills", "Soft Skills are required")
        # if education is None:
        #     self.add_error("education", "Education is required")
        # if workExperience is None:
        #     self.add_error("workExperience", "Work Experience is required")


class WorkInfoForm(forms.Form):
    form_type = forms.CharField()
    company_name = forms.CharField(label='Company Name', max_length=100, required=True )
    job_role = forms.CharField(label='Job Role', max_length=100, required=True)
    hr_name = forms.CharField(label='HR Name', max_length=100, required=False)
    job_post = forms.CharField(label='Job Post', widget=forms.Textarea, max_length=1600, required=False)
    add_more_work = forms.CharField(label='Add More', widget=forms.Textarea, max_length=1600, required=False)


