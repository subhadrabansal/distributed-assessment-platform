import re
from marshmallow import Schema, fields as ma_fields, validate, validates_schema, ValidationError



class RegisterRequestSchema(Schema):
    fullname = ma_fields.String(
        required=True,
        validate=[
            validate.Length(min=2, max=80),
            validate.Regexp(
                r"^[A-Za-z\s']+$",  # Only letters, spaces, and apostrophes
                error="Full name can only contain letters, spaces, and apostrophes."
            )
        ]
    )
    email = ma_fields.Email(
        required=True,
        validate=validate.Length(max=255)
    )
    password = ma_fields.String(
        required=True,
        validate=[
            validate.Length(min=8, max=200),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]+$',
                error="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
        ]
    )
    confirm_password = ma_fields.String(
        required=True,
        validate=validate.Length(min=8, max=200)
    )

    @validates_schema
    def validate_password_match(self, data, **kwargs):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords must match.', field_name='confirm_password')