from utils import custom_log
from flask import Blueprint,redirect
from flask_restx import Api


logger = custom_log(__name__)

auth_bp = Blueprint('auth_bp', __name__)


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

auth_namespace = auth_api.namespace('auth')
"""@oauth_authorized.connect
def redirect_to_next_url(blueprint, token):
    # set OAuth token in the token storage backend
    print("redirecting")
    blueprint.token = token
    # retrieve `next_url` from Flask's session cookie
    redirect_url ='http://localhost:5000/githubLogin/login'
    # redirect the user to `next_url`
    return redirect('githubLogin.login')"""

from .auth_view import github_api,\
    UserRegister,UserLogin,UserLogout,UserOperation,ResetPassword,TokenRefresh,GitHubAuthorize,Gitdummy


#Endpoint Registry
auth_api.add_resource(UserRegister,"/signup")
auth_api.add_resource(UserLogin,"/manualLogin")
auth_api.add_resource(UserOperation,"/useroperation/<int:user_id>")
auth_api.add_resource(ResetPassword,"/resetpassword")
auth_api.add_resource(TokenRefresh,"/nonfreshtoken")
auth_api.add_resource(UserLogout,"/logout")

github_api.add_resource(GitHubAuthorize,"/login")
github_api.add_resource(Gitdummy,"/github")


