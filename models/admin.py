import uuid

from src.common.database import Datebase


class Admin(object):
    def __init__(self, firstname, lastname, email, password, _id=None):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Datebase.find_one(collection='admins',
                                 query={'email': email})
        if data is not None:
            return cls(**data)
