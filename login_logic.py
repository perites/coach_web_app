import logging
import web_confg
from flask_login import LoginManager, UserMixin, login_user
from flask import redirect, request

login_manager = LoginManager()
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def authenticate(username, password):
    next_url = request.args.get('next')
    if (username, password) in web_confg.ADMINS:
        user = User(username)
        login_user(user)
        logging.info(f"User with username {username} was authenticated")
        return redirect(next_url) if next_url else redirect(f"/admin/sessions")

    logging.warning(f"User with username {username} was NOT authenticated")
    return redirect(f'/login?next={next_url}')
