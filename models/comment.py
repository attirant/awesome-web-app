import datetime
import uuid

from src.common.database import Datebase as Database


class Comment(object):
    def __init__(self, content, post_id, author, created_date=datetime.datetime.today(), _id=None):
        self.content = content
        self.post_id = post_id
        self.author = author
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='comments',
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'content': self.content,
            'post_id': self.post_id,
            'author': self.author,
            'created_date': self.created_date
        }

    @classmethod
    def get_comment(cls, id):
        comment_data = Database.find_one(collection='comments',
                                         query={'_id': id})
        comment = cls(**comment_data)
        comment.created_date = str(comment.created_date.ctime())
        return comment

    @staticmethod
    def get_comments(post_id):
        comments_data = [comment for comment in Database.find(collection='comments', query={'post_id': post_id})]
        comments = []
        for comment_data in comments_data:
            comments += [Comment(post_id=comment_data['post_id'],
                                 content=comment_data['content'],
                                 created_date=comment_data['created_date'],
                                 author=comment_data['author'],
                                 _id=comment_data['_id'])
                         ]
        result = []
        for comment in comments:
            result += [{
                'post_id': comment.post_id,
                'content': comment.content,
                'created_date': str(comment.created_date.ctime()),
                '_id': comment._id,
                'author': comment.author
            }]
        result.reverse()
        return result

    @staticmethod
    def remove_comment(id):
        return Database.remove(collection='comments', query={'_id': id})

    @staticmethod
    def edit_comment(id, data):
        return Database.edit(collection='comments', query={'_id': id}, data=data)
