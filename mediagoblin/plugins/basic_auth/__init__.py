# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import uuid

from mediagoblin.plugins.basic_auth import forms as auth_forms
from mediagoblin.plugins.basic_auth import tools as auth_tools
from mediagoblin.db.models import User
from mediagoblin.tools import pluginapi
from sqlalchemy import or_


def setup_plugin():
    config = pluginapi.get_config('mediagoblin.pluginapi.basic_auth')


def check_login(user, password):
    if user.pw_hash:
        result = check_password(password, user.pw_hash)
        if result:
            return result
    return None


def get_user(username):
    user = User.query.filter(
        or_(
            User.username == username,
            User.email == username,
        )).first()
    return user


def create_user(registration_form):
    user = get_user(registration_form.username.data)
    if not user and 'password' in registration_form:
        user = User()
        user.username = registration_form.username.data
        user.email = registration_form.email.data
        user.pw_hash = igen_password_hash(
            registration_form.password.data)
        user.verification_key = unicode(uuid.uuid4())
        user.save()
    return user


def get_login_form(request):
    return auth_forms.LoginForm(request.form)


def get_registration_form(request):
    return auth_forms.RegistrationForm(request.form)


def gen_password_hash(raw_pass, extra_salt):
    return auth_tools.bcrypt_gen_password_hash(raw_pass, extra_salt)


def check_password(raw_pass, stored_hash, extra_salt):
    return auth_tools.bcrypt_check_password(raw_pass, stored_hash, extra_salt)


def auth():
    return True


def append_to_global_context(context):
    context['pass_auth'] = True
    return context


def add_to_form_context(context):
    context['pass_auth_link'] = True
    return context


hooks = {
    'setup': setup_plugin,
    'authentication': auth,
    'auth_check_login': check_login,
    'auth_get_user': get_user,
    'auth_create_user': create_user,
    'auth_get_login_form': get_login_form,
    'auth_get_registration_form': get_registration_form,
    'auth_gen_password_hash': gen_password_hash,
    'auth_check_password': check_password,
    'auth_fake_login_attempt': auth_tools.fake_login_attempt,
    'template_global_context': append_to_global_context,
    ('mediagoblin.plugins.openid.register',
    'mediagoblin/auth/register.html'): add_to_form_context,
    ('mediagoblin.plugins.openid.login',
     'mediagoblin/auth/login.html'): add_to_form_context,
}
