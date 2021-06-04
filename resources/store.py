from flask_restful import Resource

from libs.strings import getText
from models.store import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200
        return {"message": getText("store_not_found")}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": getText("store_name_exists").format(name)}, 400

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": getText("store_error_inserting")}, 500

        return store_schema.dump(store), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": getText("store_deleted")}


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": store_list_schema.dump(StoreModel.find_all())}
