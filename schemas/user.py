from ma import ma
from models.user import UserModel


# todo: info passing in the UserModel here, checks the fields and ensures user object is passed back instead of dict
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "activated")
        load_instance = True

    # todo info: >> No longer needed as flask marshmallow will use the one in the model class
    # id = fields.Int()
    # username = fields.Str(required=True)
    # password = fields.Str(required=True)
