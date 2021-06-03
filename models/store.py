from typing import List

from db import db


class StoreModel(db.Model):
    __tablename__ = "store"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

    items = db.relationship("ItemModel", lazy="dynamic")  # this is lazy loading for one => many relationship

    @classmethod
    def find_by_name(cls, name) -> "StoreModel":
        return cls.query.filter_by(name=name).first()  # SELECT * FROM items WHERE name=name LIMIT 1

    @classmethod
    def find_all(cls) -> List["StoreModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
