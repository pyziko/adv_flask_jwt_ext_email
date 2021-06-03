import datetime
from typing import List

from db import db


class ItemModel(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    price = db.Column(db.Float(precision=2), nullable=False)
    request_id = db.Column(db.String(15))

    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    store = db.relationship("StoreModel")

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()  # SELECT * FROM items WHERE name=name LIMIT 1

    @classmethod
    def find_all(cls) -> List["ItemModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        print("BEFORE COMMIT: ->", self.id)
        db.session.commit()
        print("AFTER COMMIT: ->", self.id)
        self.request_id = str(datetime.date.today().strftime("%b%y%d")).upper() + "-" + str(self.id)
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
