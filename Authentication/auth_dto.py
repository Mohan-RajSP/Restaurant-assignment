from . import auth_api
from flask_restx import fields


signin_request = auth_api.model('signin_request',{
    "name":fields.String(),
    "password":fields.String(),
    "email":fields.String(),
})


sign_in_response = auth_api.model('sign_in_response',{
    "id":fields.Integer(),
    "email":fields.String(),
    "name":fields.String(),
})

signin_baseresponse = auth_api.model('signin_baseresponse',{
    "message": fields.String(),
    "user": fields.Nested(sign_in_response)
})

login_request = auth_api.model('login_request',{
    "email":fields.String(),
    "password":fields.String(),
})

login_response = auth_api.model('login_response',{
    "access_token":fields.String(),
    "refresh_token":fields.String()
})

non_refresh_token_response = auth_api.model('non_refresh_token_response',{
    "access_token":fields.String()
})
