from django import forms
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from django_otp import user_has_device, devices_for_user

from magicauth import settings as magicauth_settings
from magicauth.models import MagicToken

email_unknown_callback = import_string(magicauth_settings.EMAIL_UNKNOWN_CALLBACK)


class EmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        user_email = self.cleaned_data["email"]
        user_email = user_email.lower()

        email_field = magicauth_settings.EMAIL_FIELD
        field_lookup = {f"{email_field}__iexact": user_email}
        if not get_user_model().objects.filter(**field_lookup).exists():
            email_unknown_callback(user_email)
        return user_email


class OTPForm(forms.Form):
    OTP_NUM_DIGITS = magicauth_settings.OTP_NUM_DIGITS
    otp_token = forms.CharField(
        max_length=OTP_NUM_DIGITS,
        min_length=OTP_NUM_DIGITS,
        validators=[RegexValidator(r"^\d{6}$")],
        label=_(
            f"Enter the {OTP_NUM_DIGITS} digit code generated by your phone or OTP card"
        ),
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    def __init__(self, user, *args, **kwargs):
        super(OTPForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_otp_token(self):
        otp_token = self.cleaned_data["otp_token"]
        user = self.user
        if not user_has_device(user):
            raise ValidationError(
                _("The system could not find a device (OTP card or generator on phone) for your account."
                  "Contact support to add one.")
            )

        for device in devices_for_user(user):
            if device.verify_is_allowed() and device.verify_token(otp_token):
                return otp_token

        raise ValidationError(
            _("OTP token is not valid.")
        )
