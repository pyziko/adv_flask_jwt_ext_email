from typing import Dict, Union

from flask import request, url_for

from db import db
from requests import Response

from mail_lib.mail_gun import Mailgun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)

    confirmation = db.relationship("ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan")

    # if lazy is dynamic u can add child later as below else you will get None
    # user = UserModel(...)
    # confirmation = ConfirmationModel(...)
    # confirmation.save_to_db()
    # print(user.confirmation

    # allow us to do this   UserModel.most_recent_confirmation, rather than UserModel.most_recent_confirmation()
    @property
    def most_recent_confirmation(self) -> ConfirmationModel:
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username) -> "UserModel":
        return cls.query.filter_by(username=username).first()  # .query ==> select * from users, .filter ==> where

    @classmethod
    def find_by_email(cls, email) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def send_confirmation_email(self) -> Response:
        # root http://localhost:5000
        # confirmation is the name of the route i.e UserConfirm in lowercase
        # hence we have http://localhost:5000/user_confirm/1
        link = request.url_root[:-1] + url_for("confirmation", confirmation_id=self.most_recent_confirmation.id)

        subject = "Registration Confirmation"
        text = f"Please click the link to confirm your registration: {link}"
        html = f'<html>Please click the link to confirm your registration: <a href="{link}">{link}<a/> </html>'
        return Mailgun.send_confirmation_email([self.email], subject, text, html)

