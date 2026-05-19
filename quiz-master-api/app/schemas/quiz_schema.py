import re
from datetime import datetime
from marshmallow import Schema, fields as ma_fields, validate, validates_schema, ValidationError



class QuizRequestSchema(Schema):
    chapter_id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Chapter ID must be a positive integer.")
    )
    name = ma_fields.String(
        required=True,
        validate=[
            validate.Length(min=2, max=512),
            validate.Regexp(
                r"^[A-Za-z\s']+$", 
                error="Quiz can only contain letters, spaces and ' (e.g., Mathematics, Computer Science)."
            )
        ]
    )
    description = ma_fields.String(
        required=True,
        validate=[
            validate.Regexp(
                r'^[A-Za-z0-9 .,!?()\'":;-]+$', 
                error="Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
            )
        ]
    )
    start_date = ma_fields.String(
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

    end_date = ma_fields.String(
        required=True,
        validate=[
            validate.Regexp(
                r'^\d{2}-\d{2}-\d{4}$',
                error="Invalid date format. Use DD-MM-YYYY."
            )
        ],
        error_messages={
            'required': 'End date is required.'
        }
    )

    duration = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=30, max=120, error="Duration must be between 30 and 120 minutes.")
    )

    @validates_schema
    def validate_dates(self, data, **kwargs):
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        try:
            start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
        except (ValueError, TypeError):
            raise ValidationError({'start_date': 'Invalid date format. Use DD-MM-YYYY.'})

        if start_date.date() <= datetime.now().date():
            raise ValidationError({'start_date': 'Started date must be greater than today.'})

        try:
            end_date = datetime.strptime(end_date_str, '%d-%m-%Y')
        except (ValueError, TypeError):
            raise ValidationError({'end_date': 'Invalid date format. Use DD-MM-YYYY.'})

        if end_date <= start_date:
            raise ValidationError({'end_date': 'End date must be greater than the start date.'})

    


class QuizEditRequestSchema(Schema):
    id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="ID must be a positive integer.")
    )
    chapter_id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Chapter ID must be a positive integer.")
    )
    name = ma_fields.String(
    required=True,
    validate=[
        validate.Length(min=2, max=512),
        validate.Regexp(
            r"^[A-Za-z\s']+$", 
            error="Quiz Name can only contain letters, spaces and ' (e.g., Mathematics, Computer Science)."
        )
    ])
    description = ma_fields.String(
        required=True,
        validate=[
            validate.Regexp(
                r'^[A-Za-z0-9 .,!?()\'":;-]+$', 
                error="Description can contain letters, numbers, spaces, and common punctuation (.,!?()'\":;-)."
            )
    ])
    start_date = ma_fields.String(
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

    end_date = ma_fields.String(
        required=True,
        validate=[
            validate.Regexp(
                r'^\d{2}-\d{2}-\d{4}$',
                error="Invalid date format. Use DD-MM-YYYY."
            )
        ],
        error_messages={
            'required': 'End date is required.'
        }
    )
    duration = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=30, max=120, error="Duration must be between 30 and 120 minutes.")
    )
    @validates_schema
    def validate_dates(self, data, **kwargs):
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        try:
            start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
        except (ValueError, TypeError):
            raise ValidationError({'start_date': 'Invalid date format. Use DD-MM-YYYY.'})

        if start_date.date() <= datetime.now().date():
            raise ValidationError({'start_date': 'Started date must be greater than today.'})

        try:
            end_date = datetime.strptime(end_date_str, '%d-%m-%Y')
        except (ValueError, TypeError):
            raise ValidationError({'end_date': 'Invalid date format. Use DD-MM-YYYY.'})

        if end_date <= start_date:
            raise ValidationError({'end_date': 'End date must be greater than the start date.'})

