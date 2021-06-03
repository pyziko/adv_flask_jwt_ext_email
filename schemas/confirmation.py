from ma import ma
from models.confirmation import ConfirmationModel


class ConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",)   # dont return to user
        dump_only = ("id", "expired_at", "confirmed")      # not needed to be passed
        include_fk = True
        load_instance = True
