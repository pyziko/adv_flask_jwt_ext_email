import hmac
import traceback

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt

from libs.mail_gun import MailGunException
from libs.strings import getText
from models.confirmation import ConfirmationModel
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())     # errors are caught in app.py as general validation err handler

        if UserModel.find_by_username(user.username):
            return {"message": getText("user_username_exists")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": getText("user_email_exists")}, 400

        try:

            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()   # lazy=dynamic handy saving child(confirmation) after user was created before
            user.send_confirmation_email()
            return {"message": getText("user_registered")}, 201

        except MailGunException as err:
            user.delete_from_db() # rollback
            return {"message": str(err)}, 500
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()
            return {"message": getText("user_error_creating")}, 500


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": getText("user_not_found")}, 404
        return user_schema.dump(user), 200    # the dump converts directly into dictionary

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": getText("user_not_found")}, 404
        user.delete_from_db()
        return {"message": getText("user_deleted")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):

        user_json = request.get_json()
        # errors are caught in app.py as general validation err handler
        # email will be ignored, by using partial
        user_data = user_schema.load(user_json, partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        # this is what the `authenticate()` function did in security.py
        if user and hmac.compare_digest(user.password, user_data.password):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"message": getText("user_not_confirmed").format(user.username)}, 400

        return {"message": getText("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        sub = get_jwt()["sub"]
        BLACKLIST.add(jti)
        return {"message": getText("user_logged_out").format(sub)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

