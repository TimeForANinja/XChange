from apiflask import Schema
from apiflask.fields import String, Integer, Boolean, File
from apiflask.validators import OneOf, Length
from marshmallow import validates_schema, ValidationError


class CreateItemSchema(Schema):
    type = String(required=True, validate=OneOf(['text', 'file', 'link']))
    content = String()
    name_type = String(load_default='human', validate=OneOf(['base64', 'human']))
    access_limit = Integer(load_default=0, validate=OneOf([0, 1, 10, 100]))
    time_limit = String(load_default='unlimited', validate=OneOf(['1d', '7d', '30d', 'unlimited']))
    fast_forward = Boolean(load_default=True)
    syntax = String(load_default='plain')
    file = File()

    @validates_schema
    def validate_inputs(self, data: dict, **kwargs):
        if data['type'] in ['text', 'link']:
            if not data.get('content') or not data['content'].strip():
                raise ValidationError('Content cannot be empty for text or link items', 'content')
        if data['type'] == 'file' and not data.get('file'):
            # Note: APIFlask might not always populate 'file' in 'data' if it's missing from request
            # but it should be present if it's in the schema and location includes 'files'
            raise ValidationError('A file must be provided for file items', 'file')

class ConfigSchema(Schema):
    ENABLE_ADMIN_UI = Boolean()
    ENABLE_UNLIMITED_USAGE = Boolean()
    ENABLE_UNLIMITED_AGE = Boolean()
    ENABLE_FAST_FORWARD = Boolean()
    MAX_FILE_SIZE = Integer()
    VERSION = String()

class ItemResponseSchema(Schema):
    id = String()
    base_host = String()
    path = String()
    uri = String()
    raw_uri = String()
    message = String() # For errors

class ItemDetailSchema(Schema):
    id = String()
    type = String()
    access_limit = Integer()
    access_count = Integer()
    last_access = String()
    created_at = String()
    expires_at = String()
    content = String()
    syntax = String()
    filename = String()
    mimetype = String()
    base_host = String()
    path = String()
    uri = String()
    raw_uri = String()

class AdminItemSchema(Schema):
    id = String()
    type = String()
    access_limit = Integer()
    access_count = Integer()
    last_access = String()
    created_at = String()
    expires_at = String()
    file_id = String()
    filename = String()
    content = String()
    syntax = String()
    fast_forward = Boolean()
    uri = String()
    raw_uri = String()

class UpdateItemSchema(Schema):
    id = String(validate=Length(min=1))
    access_limit = Integer(validate=OneOf([0, 1, 10, 100]))
    time_limit = String(validate=OneOf(['1d', '7d', '30d', 'unlimited']))

class MessageSchema(Schema):
    message = String()
