"""Routes for user authentication."""
from flask import redirect,request,url_for
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    fresh_jwt_required,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,jwt_optional
)
from login.utils import custom_response,field_check
from .auth_model import User_schema, User
from . import logger, auth_namespace
from login.strings.error_constants import Errors
from flask_restx import Resource, Api
from flask import Blueprint
from flask import current_app as app
from flask_dance.contrib.github import make_github_blueprint, github
from login import db, jwt
from .auth_dto import signin_baseresponse, signin_request,login_request,login_response, non_refresh_token_response

blacklist = set()
user_schema = User_schema()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    print("useradd",user)
    return {'Id': user}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user

class UserRegister(Resource):

    @auth_namespace.expect(signin_request)
    @auth_namespace.response(200,"OK",signin_baseresponse)
    def post(self):
        try:
            req_data = request.get_json()
            loaded_data = user_schema.load(req_data, session=db.session)
            existing_user = User.query.filter_by(email=loaded_data["email"]).first()

            if existing_user:
                out = {"message": "User already exist"}
                return out, 400
            user = User(loaded_data)
            user.save_user()
            dumped_data = user_schema.dump(user)
            out = {"message": "CREATED", "user": dumped_data}
            return out, 200

        except ValidationError as vError:
            logger.exception("The exception is {}".format(vError.messages))
            out = {"message": vError.messages}
            return out, 400

        except Exception as Other_err:
            db.session.rollback()
            logger.exception("The exception is {}".format(Other_err))
            out = {"message": Other_err.args}
            return out, 500


class UserLogin(Resource):

    @auth_namespace.expect(login_request)
    @auth_namespace.response(200,"OK",login_response)
    def post(self):
        try:
            user_data = request.get_json()
            fields = ("email","password")
            field_check(fields, user_data)
            user = User.find_by_mail_id(user_data["email"])
            if user:
                if not user.check_password(None) :
                    if user and user.check_password(user_data["password"]):
                        access_token = create_access_token(identity=user.id, fresh=True)
                        refresh_token = create_refresh_token(identity=user.id)
                        return {"access_token": access_token, "refresh_token": refresh_token}, 200
                    else:
                        return {"message": Errors.user_invalid_credentials}, 401
                else:
                    access_token = create_access_token(identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(user)
                    return {"access_token": access_token, "refresh_token": refresh_token}, 200
            else:
                return{"message":Errors.user_not_found}, 400

        except Exception as Other_err:
            db.session.rollback()
            logger.exception("The exception is {}".format(Other_err))
            out = {"message": Other_err.args}
            return out, 500


class TokenRefresh(Resource):
    @auth_namespace.doc(security='apikey')
    @auth_namespace.response(200, 'OK',non_refresh_token_response)
    @jwt_refresh_token_required
    def post(self):
        """ Creates a non-fresh token. The input should be "Bearer {refreshToken}" format"""

        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200


#disable only the refresh token
class UserLogout(Resource):
    @auth_namespace.doc(security='apikey')
    @jwt_required
    def delete(self):
        """
        Step: Logs out the user who owns the token passed in the header
        Either fresh or non-fresh token needs to be passed
        """
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return ({"msg": "Successfully logged out"}), 200


class UserOperation(Resource):
    @auth_namespace.doc(security='apikey')
    @jwt_required
    def get(self, user_id: int):
        try:
            user = User.find_by_id(user_id)
            if not user:
                return {"message": Errors.user_not_found}, 404

            return user_schema.dump(user), 200

        except Exception as Other_err:
            logger.exception("The exception is {}".format(Other_err))
            out = {"message": Other_err.args}
            return custom_response(out), 500

    @auth_namespace.doc(security='apikey')
    @fresh_jwt_required
    def delete(self, user_id: int):
        """A fresh jwt token is required, if not logged in, log in and get the access token and pass it to the header
        with "Bearer" prefixed"""
        try:
            user = User.find_by_id(user_id)
            if not user:
                return {"message": Errors.user_not_found}, 404

            user.delete_from_db()
            return {"message": Errors.user_deleted}, 200

        except Exception as Other_err:
            db.session.rollback()
            logger.exception("The exception is {}".format(Other_err))
            out = {"message": Other_err.args}
            return custom_response(out), 500


class ResetPassword(Resource):

    @auth_namespace.doc(security='apikey')
    @fresh_jwt_required
    def post(self):
        req_data = request.get_json()
        loaded_obj = user_schema.load(req_data)
        user = User.find_by_mail_id(loaded_obj.email)
        if not user:
            return {"message": Errors.user_invalid_credentials}, 400

        user.set_password(req_data["password"])
        user.save_to_db()
        return {"message": Errors.user_password_reset}, 201

#OAuth


class GitHubAuthorize(Resource):
    def get(self):
        try:
            if not github.authorized:
                return redirect(url_for('github.login'))
            account_info = github.get('/user')
            if account_info.ok:
                user_data = account_info.json()
                email = user_data.get("email", None)
                name = user_data.get("name", None)
                if User.find_by_mail_id(email):
                    return {"message": Errors.user_username_exists}, 400
                else:
                    loaded_data = user_schema.load({"email":email,"name":name,"password":None}, session=db.session)
                    user= User(loaded_data)
                    user.save_user()
                    dumped_data = user_schema.dump(user)
                    return {"message":"CREATED", "user":dumped_data}, 200
            return {"message": Errors.user_invalid_credentials}, 400

        except ValidationError as vError:
            db.session.rollback()
            logger.exception("The exception is {}".format(vError.messages))
            out = {"message": vError.messages}
            return custom_response(out), 400


class Gitdummy(Resource):
    @jwt_required
    def get(self):
        return "Hello"


