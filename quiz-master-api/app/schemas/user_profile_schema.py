from marshmallow import Schema, fields as ma_fields, validate, validates_schema, ValidationError
import re
from datetime import datetime


class UserProfileRequestSchema(Schema):
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
    phone_number = ma_fields.String(
        required=False, 
        allow_none=True, 
        validate=[
            validate.Length(max=15),
            validate.Regexp(
                r'^\+?[1-9]\d{1,14}$',  # E.164 format
                error="Phone number must be in E.164 format (e.g., +911234567890)."
            )
        ],
        error_messages={
            'required': 'Phone number is required.'
        }
    )
    date_of_birth = ma_fields.String(
        required=True,
        validate=[
            validate.Regexp(
                r'^\d{2}-\d{2}-\d{4}$',
                error="Invalid date format. Use DD-MM-YYYY."
            )
        ],
        error_messages={
            'required': 'Started date is required.'
        }
    )
    qualification = ma_fields.String(
        required=False, 
        allow_none=True, 
        validate=[
            validate.Length(max=512),
            validate.Regexp(
                r"^[A-Za-z\s']+$",  
                error="Qualification can only contain letters, spaces, and apostrophes."
            )
        ]
    )
    subject = ma_fields.String(
        required=False, 
        allow_none=True, 
        validate=[
            validate.Length(max=512),
            validate.Regexp(
                r"^[A-Za-z\s']+$",  
                error="Subject can only contain letters, spaces, and apostrophes."
            )
        ]
    )

    @validates_schema
    def validate_dates(self, data, **kwargs):
        date_of_birth_str = data.get('date_of_birth')
        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%d-%m-%Y')
        except (ValueError, TypeError):
            raise ValidationError({'date_of_birth': 'Invalid date format. Use DD-MM-YYYY.'})
        if date_of_birth > datetime.now():
            raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future.'})
        if date_of_birth.year < 1900:
            raise ValidationError({'date_of_birth': 'Date of birth cannot be before 1900.'})
        if date_of_birth.year > datetime.now().year - 14:
            raise ValidationError({'date_of_birth': 'User must be at least 14 years old.'})

