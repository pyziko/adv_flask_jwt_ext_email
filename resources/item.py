from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from libs.strings import getText
from models.item import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item)   # dump:::object to dict
        return {"message": getText("item_not_found")}, 404

    # This ensures that a new item can be created wen u just logged in- fresh_toke_required
    # NOTE the parameter fresh, not refresh
    # Usage: to ensure a critical action requires user logging in or entering their password
    @jwt_required(fresh=True)
    def post(self, name: str):  # /item/chair
        if ItemModel.find_by_name(name):
            return {"message": getText("item_name_exists").format(name)}, 400

        item_json = request.get_json()  # other info, price, store_id
        item_json["name"] = name

        item = item_schema.load(item_json)  # errors are caught in app.py as general validation err handler

        try:
            item.save_to_db()
        except:
            return {"message": getText("item_error_inserting")}, 500  # Internal Server Error

        return item_schema.dump(item), 201

    @classmethod    # this mus come first
    @jwt_required()
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": getText("item_deleted")}
        return {"message": ITEM_NOT_FOUND}

    @classmethod
    def put(cls, name: str):
        item_json = request.get_json()

        item = ItemModel.find_by_name(name)

        if item is None:
            item_json["name"] = name
            item = item_schema.load(item_json)  # errors are caught in app.py as general validation err handler

        else:
            item.price = item_json["price"]

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
