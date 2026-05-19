import re
from datetime import datetime
from marshmallow import Schema, fields as ma_fields, validate, validates_schema, ValidationError

class QuestionRequestSchema(Schema):
    quiz_id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Quiz ID must be a positive integer.")
    )
    question = ma_fields.String(
        required=True,
        validate=validate.Length(min=2, max=4096)
    )
    option1 = ma_fields.String(
        required=True,
        validate=validate.Length(min=2, max=4096)
    )
    option2 = ma_fields.String(
        required=True,
        validate=validate.Length(min=2, max=4096)
    )
    option3 = ma_fields.String(
        required=True,
        validate=validate.Length(min=2, max=4096)
    )
    option4 = ma_fields.String(
        required=True,
        validate=validate.Length(min=2, max=4096)
    )
    answer = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=4, error="Answer must be between 1 and 4.")
    )
    marks = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=5 ,error="Marks must be between 1 and 5.")
    )

class QuestionEditRequestSchema(Schema):
    id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="ID must be a positive integer.")
    )
    quiz_id = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Quiz ID must be a positive integer.")
    )
    question = ma_fields.String(
        required=True,
        validate=validate.Length(min=1, max=4096)
    )
    option1 = ma_fields.String(
        required=True,
        validate=validate.Length(min=1, max=4096)
    )
    option2 = ma_fields.String(
        required=True,
        validate=validate.Length(min=1, max=4096)
    )
    option3 = ma_fields.String(
        required=True,
        validate=validate.Length(min=1, max=4096)
    )
    option4 = ma_fields.String(
        required=True,
        validate=validate.Length(min=1, max=4096)
    )
    answer = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=4, error="Answer must be between 1 and 4.")
    )
    marks = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=5 ,error="Marks must be between 1 and 5.")
    )

    @validates_schema
    def validate_answer(self, data, **kwargs):
        answer = data.get('answer')
        marks = data.get('marks')
        if marks < 1 or marks > 5:
            raise ValidationError("Marks must be between 1 and 5.", field_name='marks')
        if answer not in [1, 2, 3, 4]:
            raise ValidationError("Answer must be between 1 and 4.", field_name='answer')
