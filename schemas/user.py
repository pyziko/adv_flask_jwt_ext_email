from ma import ma
from marshmallow import pre_dump
from models.user import UserModel


# todo: info passing in the UserModel here, checks the fields and ensures user object is passed back instead of dict
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)   # don't include when returning to user
        dump_only = ("id", "confirmation")  # not needed when passing data for creation
        include_relationships = True
        load_instance = True

    # called before dumping
    # ensuring to send back only the most_recent_confirmation
    @pre_dump   # not we have post_dump, pre_load, post_load
    def _pre_dump(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user

