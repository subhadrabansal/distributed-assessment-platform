from marshmallow import fields as ma_fields, validate, Schema

class LoginRequestSchema(Schema):
    email = ma_fields.Email(required=True, validate=validate.Length(max=255))
    password = ma_fields.String(required=True, validate=validate.Length(min=8))