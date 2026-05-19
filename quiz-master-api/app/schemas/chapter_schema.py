import re
from marshmallow import Schema, fields as ma_fields, validate, validates_schema, ValidationError



class ChapterRequestSchema(Schema):
    subject_id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Subject ID must be a positive integer.")
    )
    name = ma_fields.String(
        required=True,
        validate=[
            validate.Length(min=2, max=512),
            validate.Regexp(
                r"^[A-Za-z\s']+$", 
                error="Chapter can only contain letters, spaces and ' (e.g., Mathematics, Computer Science)."
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
    

class ChapterEditRequestSchema(Schema):
    id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="ID must be a positive integer.")
    )
    
    subject_id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Subject ID must be a positive integer.")
    )
    
    name = ma_fields.String(
    required=True,
    validate=[
        validate.Length(min=2, max=512),
        validate.Regexp(
            r"^[A-Za-z\s']+$", 
            error="Subject can only contain letters, spaces and ' (e.g., Mathematics, Computer Science)."
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
