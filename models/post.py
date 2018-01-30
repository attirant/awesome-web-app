import uuid
import datetime

from src.common.database import Datebase as Database


class Post(object):
    def __init__(self, title, content, author, created_date=datetime.datetime.today(), _id=None):
        self.title = str(title).strip()
        self.content = str(content).strip()
        self.author = str(author).strip()
        self.created_date = created_date
        self._id = str(uuid.uuid4().hex) if _id is None else str(_id)

    def save_to_mongo(self):
        Database.insert(collection='posts',
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'author': self.author,
            'content': self.content,
            'title': self.title,
            'created_date': self.created_date
        }

    @classmethod
    def get_post(cls, id):
        post_data = Database.find_one(collection='posts', query={'_id': id})
        post = cls(**post_data)
        post.created_date = str(post.created_date.ctime())
        return post

    @staticmethod
    def get_posts_by_author(author):
        posts_data = [post for post in Database.find(collection='posts', query={'author': author})]
        posts = []
        for post_data in posts_data:
            s = str(post_data['content'])
            if len(s) < 750:
                posts += [Post(title=post_data['title'],
                               content=s,
                               author=post_data['author'],
                               created_date=post_data['created_date'],
                               _id=post_data['_id'])]
            else:
                limit = 750
                for i in range(limit, 0, -1):
                    if s[i] is " ":
                        limit = i
                        break

                s = s[:limit]

                posts += [Post(title=post_data['title'],
                               content=s + " ...",
                               author=post_data['author'],
                               created_date=post_data['created_date'],
                               _id=post_data['_id'])]
        result = []
        for post in posts:
            result += [{
                'title': str(post.title).strip(),
                'content': str(post.content).strip(),
                'author': str(post.author).strip(),
                'created_date': str(post.created_date.ctime()),
                '_id': str(post._id).strip()
            }]
        result.reverse()
        return result

    @staticmethod
    def get_posts():
        posts_data = [post for post in Database.find(collection='posts', query={})]
        posts = []
        for post_data in posts_data:
            s = str(post_data['content'])
            if len(s) < 750:
                posts += [Post(title=post_data['title'],
                               content=s,
                               author=post_data['author'],
                               created_date=post_data['created_date'],
                               _id=post_data['_id'])]
            else:
                limit = 750
                for i in range(limit, 0, -1):
                    if s[i] is " ":
                        limit = i
                        break

                s = s[:limit]

                posts += [Post(title=post_data['title'],
                               content=s + " ...",
                               author=post_data['author'],
                               created_date=post_data['created_date'],
                               _id=post_data['_id'])]
        result = []
        for post in posts:
            result += [{
                'title': str(post.title).strip(),
                'content': str(post.content).strip(),
                'author': str(post.author).strip(),
                'created_date': str(post.created_date.ctime()),
                '_id': str(post._id).strip()
            }]
        result.reverse()
        return result

    @staticmethod
    def count_post_by_author(author):
        posts = Post.get_posts()
        c = 0
        for post in posts:
            if "author" in post:
                if post['author'] == author:
                    c = c + 1
        return c

    @staticmethod
    def remove_post(id):
        return Database.remove(collection='posts', query={'_id': id})

    @staticmethod
    def remove_post_by_author(author):
        posts = Post.get_posts()
        for post in posts:
            if "author" in post:
                if post['author'] == author:
                    Post.remove_post(post['_id'])

    @staticmethod
    def edit_post(id, data):
        return Database.edit(collection='posts', query={'_id': id}, data=data)

    @classmethod
    def not_exists(cls, posts, post):
        for p in posts:
            if cls(**p).created_date == cls(**post).created_date:
                return False

        return True

    @staticmethod
    def remove_duplicates(posts_list):
        posts = []
        for post in posts_list:
            if Post.not_exists(posts, post):
                posts.append(post)
        return posts

    @staticmethod
    def search(string):
        string = str(string).strip()
        posts_data = [post for post in Database.find(collection='posts',
                                                     query={"title": {'$regex': ".*" + string.capitalize() + ".*"}})]
        posts_data += [post for post in Database.find(collection='posts',
                                                     query={"title": {'$regex': ".*" + string + ".*"}})]
        posts_data = Post.remove_duplicates(posts_data)
        posts = []
        for post_data in posts_data:
            s = str(post_data['content'])
            if len(s) < 750:
                posts += [Post(title=post_data['title'],
                               content=s,
                               author=post_data['author'],
                               created_date=post_data['created_date'],
                               _id=post_data['_id'])]
            else:
                limit = 750
                for i in range(limit, 0, -1):
                    if s[i] is " ":
                        limit = i
                        break

                s = s[:limit]

                posts += [Post(title=post_data['title'],
                               content=s + " ...",
                               author=post_data['author'],
                               created_date=post_data['created_date'],
                               _id=post_data['_id'])]
        result = []
        for post in posts:
            result += [{
                'title': post.title,
                'content': post.content,
                'author': post.author,
                'created_date': str(post.created_date.ctime()),
                '_id': post._id
            }]
        result.reverse()
        return result
