from utils import custom_log
from flask import Blueprint
from flask_restx import Api
from flask_dance.contrib.github import make_github_blueprint
from flask import current_app as app

logger = custom_log(__name__)

auth_bp = Blueprint('auth_bp', __name__)

github_blueprint = make_github_blueprint(client_id=app.config['GITLAB_OAUTH_CLIENT_ID'],
                                        client_secret=app.config['GITLAB_OAUTH_CLIENT_SECRET'],
                                         scope=['openid', 'email', 'profile'],)
                                         #redirect_url ='http://localhost:5000/githubLogin/login',


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

auth_api = Api(auth_bp,
               default='Restaurant',
               default_label='This is the Authorization Api service',
               version='0.0.1',
               title='Authorization API with Python',
               description="SignUp, Login, Logout",
               ordered=False,
               authorizations=authorizations,
               )

github_api = Api(github_blueprint)

auth_namespace = auth_api.namespace('auth')

from .auth_view import UserRegister,UserLogin,UserLogout,UserOperation,ResetPassword,TokenRefresh,GitHubAuthorize,Gitdummy


#Endpoint Registry
auth_api.add_resource(UserRegister,"/signup")
auth_api.add_resource(UserLogin,"/manualLogin")
auth_api.add_resource(UserOperation,"/useroperation/<int:user_id>")
auth_api.add_resource(ResetPassword,"/resetpassword")
auth_api.add_resource(TokenRefresh,"/nonfreshtoken")
auth_api.add_resource(UserLogout,"/logout")

github_api.add_resource(GitHubAuthorize,"/Github")
github_api.add_resource(Gitdummy,"/login1")


