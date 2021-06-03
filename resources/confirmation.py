import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from mail_lib.mail_gun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from resources.user import USER_NOT_FOUND
from schemas.confirmation import ConfirmationSchema

NOT_FOUND = "Confirmation reference not found"
EXPIRED = "The link has expired"
ALREADY_CONFIRMED = "Registration has already been confirmed"
RESEND_SUCCESSFUL = "Email confirmation successfully re-sent"
RESEND_FAILED = "Internal server error, Failed to resend confirmation email"

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Return confirmation HTML page."""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404

        if confirmation.expired:
            return {"message": EXPIRED}, 400

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=confirmation.user.email), 200, headers)
        # todo info in we intent to load a page from another location
        # return redirect("http://localhost:300", code=302)


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """Returns confirmations for a given user. USe for testing."""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        return {
                   "current_time": int(time()),
                   "confirmation": [
                       confirmation_schema.dump(each)
                       for each in user.confirmation.order_by(ConfirmationModel.expire_at).all()
                   ],
               }, 200

    @classmethod
    def post(cls, user_id: int):
        """Resend confirmation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            # lazy=dynamic comes in handy here, as we are saving after user has been created before
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": RESEND_SUCCESSFUL}, 201
        except MailGunException as err:
            return {"message": str(err)}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAILED}, 500





