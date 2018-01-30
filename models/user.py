import datetime
import uuid

from flask import session

from src.common.database import Datebase as Database
from src.common.database import Datebase
from src.models.admin import Admin
from src.models.post import Post


class User(object):
    def __init__(self, firstname, lastname, email, password, _id=None):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Datebase.find_one(collection='users',
                                 query={'email': email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Datebase.find_one(collection='users',
                                 query={'_id': _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def register(cls, firstname, lastname, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(firstname, lastname, email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def get_posts(self):
        return Post.get_posts_by_author(self.firstname)

    @staticmethod
    def is_admin(email):
        admin = Admin.get_by_email(email)
        if admin is not None:
            return True
        return False

    @staticmethod
    def get_users():
        users_data = [post for post in Database.find(collection='users', query={})]
        users = []
        for user_data in users_data:
            users += [User(firstname=user_data['firstname'],
                           lastname=user_data['lastname'],
                           email=user_data['email'],
                           password=user_data['password'],
                           _id=user_data['_id'])]
        result = []
        for user in users:
            if User.is_admin(user.email):
                result += [{
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'email': user.email,
                    'admin': "admin",
                    'password': user.password,
                    '_id': user._id
                }]
            else:
                result += [{
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'email': user.email,
                    'admin': "",
                    'password': user.password,
                    '_id': user._id
                }]

        result.reverse()
        return result

    def new_post(self, title, content, date=datetime.datetime.utcnow()):
        post = Post(title=title,
                    content=content,
                    author=self.firstname,
                    created_date=date)
        post.save_to_mongo()

    def _json(self):
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            '_id': self._id,
            'password': self.password
        }

    def save_to_mongo(self):
        Datebase.insert(collection='users',
                        data=self._json())

    @staticmethod
    def remove_user(id):
        Database.remove(collection='admins', query={'_id': id})
        return Database.remove(collection='users', query={'_id': id})

