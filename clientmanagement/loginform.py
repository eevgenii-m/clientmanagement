from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth import forms as auth_forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible


class MyAuthLoginForm(auth_forms.AuthenticationForm):
    rcaptcha = ReCaptchaField(label='', required=True, widget=ReCaptchaV2Invisible)

    def __init__(self, *args, **kwargs):
        super(MyAuthLoginForm, self).__init__(*args, **kwargs)
        if (settings.CANCEL_CAPTCHA):
            self.fields.pop('rcaptcha')
        # Relabel username field to "Email"
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'email',
            'type': 'email',
        })


class my_reset_password_form(auth_forms.PasswordResetForm):
    rcaptcha = ReCaptchaField(label='', required=True, widget=ReCaptchaV2Invisible)

    def __init__(self, *args, **kwargs):
        super(my_reset_password_form, self).__init__(*args, **kwargs)
        if (settings.CANCEL_CAPTCHA):
            self.fields.pop('rcaptcha')
