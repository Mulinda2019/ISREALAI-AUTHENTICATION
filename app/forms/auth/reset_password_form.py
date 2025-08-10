"""Password reset forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class ResetRequestForm(FlaskForm):
    """Form used to request a password reset email."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    """Form used to set a new password after following the reset link."""

    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, message="Too short")]
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")

