from flask import Flask, render_template, request, session, make_response

from src.models.admin import Admin
from src.models.comment import Comment
from src.models.post import Post
from src.models.user import User
from src.common.database import Datebase
import datetime

app = Flask(__name__)
app.secret_key = "attirant"


def is_admin():
    try:
        email = session['email']
        admin = Admin.get_by_email(email)
        if admin is not None:
            return True
        return False
    except KeyError:
        return False


app.jinja_env.globals.update(is_admin=is_admin)


@app.route('/')
def posts():
    try:
        return render_template('posts.html',
                               posts=Post.get_posts(),
                               session_email=session['email'])
    except KeyError:
        pass
    return render_template('posts.html',
                           posts=Post.get_posts(),
                           session_email=None)


@app.route('/login')
def login_template():
    try:
        if session['email'] is not None:
            return render_template('posts.html',
                                   posts=Post.get_posts(),
                                   session_email=session['email'],
                                   error="You are already logged in.")
    except KeyError:
        pass
    return render_template('login.html',
                           error="")


@app.route('/register')
def register_template():
    try:
        if session['email'] is not None:
            return render_template('posts.html',
                                   posts=Post.get_posts(),
                                   session_email=session['email'],
                                   error="You are already logged in.")

    except KeyError:
        pass
    return render_template('register.html')


@app.route('/profile')
def profile_template():
    try:
        if session['email'] is not None:
            user = User.get_by_email(session['email'])
            return render_template('profile.html',
                                   firstname=user.firstname,
                                   lastname=user.lastname,
                                   email=user.email)
    except KeyError:
        pass
    return render_template('posts.html',
                           error="You need to be logged in.",
                           posts=Post.get_posts(),
                           session_email=None)


@app.route('/logout')
def logout_template():
    try:
        if session['email'] is None:
            return render_template('posts.html',
                                   posts=Post.get_posts(),
                                   session_email=None,
                                   error="You are already logged out.")
        user = User.get_by_email(session['email'])
        user.logout()
        return render_template('logout.html',
                               firstname=user.firstname + " " + user.lastname,
                               session_email=session['email'])
    except KeyError:
        pass
    return render_template('posts.html',
                           session_email=None,
                           error="You need to be logged in.",
                           posts=Post.get_posts())


@app.before_first_request
def initialize_database():
    Datebase.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    session['email'] = None

    if User.login_valid(email, password):
        User.login(email)
        user = User.get_by_email(email)
        session['email'] = email
        return render_template('profile.html',
                               firstname=user.firstname,
                               lastname=user.lastname,
                               email=user.email)
    else:
        session['email'] = None
        return render_template('login.html',
                               error="Email address or password isn't correct.")


@app.route('/auth/register', methods=["POST"])
def register_user():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    User.register(firstname=firstname, lastname=lastname, email=email, password=password)
    return render_template('profile.html', firstname=firstname)


# posts
@app.route('/posts/<string:post_id>')
def get_post(post_id):
    try:
        post = Post.get_post(post_id)
        if post is not None:
            return render_template('post.html',
                                   post=post,
                                   comments=Comment.get_comments(post_id),
                                   session_email=session['email'])
        return render_template('posts.html',
                               posts=Post.get_posts(),
                               session_email=session['email'],
                               error="There is no post by this id.")
    except KeyError:
        return render_template('post.html',
                               comments=Comment.get_comments(post_id),
                               post=Post.get_post(post_id),
                               session_email=None)


@app.route('/posts/remove/<string:post_id>')
def remove_post(post_id):
    try:
        if session['email'] is not None:
            user_email = session['email']
            post = Post.get_post(post_id)
            if user_email == post.author or is_admin():
                Post.remove_post(post_id)
                return render_template('posts.html',
                                       error="The post removed successfully.",
                                       posts=Post.get_posts(),
                                       session_email=session['email'])

            return render_template('posts.html',
                                   error="This post doesn't belong to you.",
                                   posts=Post.get_posts(),
                                   session_email=session['email'])
    except KeyError:
        return render_template('posts.html',
                               error="You need to <a href='/login'>Log in</a>.",
                               posts=Post.get_posts(),
                               session_email=None)


@app.route('/posts/edit/<string:post_id>')
def edit_post(post_id):
    try:
        if session['email'] is not None:
            user_email = session['email']
            post = Post.get_post(post_id)
            if user_email == post.author or is_admin():
                return render_template('edit_post.html',
                                       session_email=session['email'],
                                       post=post)

            return render_template('posts.html',
                                   error="This post doesn't belong to you.",
                                   posts=Post.get_posts(),
                                   session_email=session['email'])
    except KeyError:
        return render_template('posts.html',
                               error="You need to <a href='/login'>Log in</a>.",
                               posts=Post.get_posts(),
                               session_email=None)


@app.route('/posts/edit', methods=['POST', 'GET'])
def edit2_post():
    if request.method == 'GET':
        return make_response(posts())
    else:
        title = request.form['title']
        content = request.form['content']
        _id = request.form['post_id']
        Post.edit_post(id=_id,
                       data={
                           'title': title,
                           'content': content,
                           'created_date': datetime.datetime.today()
                       }
                       )
        return make_response(posts())


@app.route('/posts/new', methods=['POST', 'GET'])
def create_new_post():
    try:
        if request.method == 'GET':
            return render_template('new_post.html')
        else:
            title = request.form['title']
            content = request.form['content']
            user = User.get_by_email(session['email'])
            new_post = Post(title, content, user.email)
            new_post.save_to_mongo()
            return make_response(posts())
    except KeyError:
        return make_response(posts())


@app.route('/posts/author/<string:author>')
def author_posts(author):
    post = Post.get_posts_by_author(author)
    error = str(author) + " has " + str(Post.count_post_by_author(author)) + " records."
    try:
        return render_template('posts.html',
                               error=error,
                               posts=post,
                               session_email=session['email'])
    except KeyError:
        return render_template('posts.html',
                               error=error,
                               posts=post,
                               session_email=None)


# comments
@app.route('/comments/new', methods=['POST', 'GET'])
def create_new_comment():
    post_id = request.form['post_id']
    if request.method == 'GET':
        return render_template('post.html',
                               post=Post.get_post(post_id))
    else:
        try:
            author = session['email']
            content = request.form['content_comment']
            new_comment = Comment(content=content,
                                  post_id=post_id,
                                  author=author)
            new_comment.save_to_mongo()
            return render_template('post.html',
                                   comments=Comment.get_comments(post_id),
                                   post=Post.get_post(post_id))
        except KeyError:
            return render_template('post.html',
                                   error="You need to log in.",
                                   post=Post.get_post(post_id),
                                   comments=Comment.get_comments(post_id),
                                   session_email=None)


@app.route('/comments/remove/<string:_id>')
def remove_comment(_id):
    comment = Comment.get_comment(_id)
    try:
        if session['email'] is not None:
            user_email = session['email']
            if user_email == comment.author or is_admin():
                Comment.remove_comment(_id)
                return render_template('post.html',
                                       error="The comment removed successfully.",
                                       post=Post.get_post(comment.post_id),
                                       comments=Comment.get_comments(comment.post_id),
                                       session_email=session['email'])

            return render_template('post.html',
                                   error="The comment doesn't belong to you.",
                                   post=Post.get_post(comment.post_id),
                                   comments=Comment.get_comments(comment.post_id),
                                   session_email=session['email'])
    except KeyError:
        return render_template('post.html',
                               error="You need to <a href='/login'>Log in</a>.",
                               post=Post.get_post(comment.post_id),
                               session_email=None)


# users
@app.route('/users')
def users():
    try:
        session_em = session['email']
        return render_template('users.html',
                               users=User.get_users(),
                               session_email=session_em)
    except KeyError:
        return render_template('users.html',
                               users=User.get_users(),
                               session_email=None)


@app.route('/users/remove/<_id>')
def remove_user(_id):
    try:
        if session['email'] is not None:
            user = User.get_by_id(_id)
            if is_admin():
                Post.remove_post_by_author(user.email)
                User.remove_user(_id)
                return render_template('users.html',
                                       error="The user removed successfully.",
                                       users=User.get_users(),
                                       session_email=session['email'])

            return render_template('users.html',
                                   error="You're not admin.",
                                   users=User.get_users(),
                                   session_email=session['email'])
    except KeyError:
        return render_template('users.html',
                               error="You need to <a href='/login'>Log in</a> as admin.",
                               users=User.get_users(),
                               session_email=None)


# search
@app.route('/search')
def search():
    try:
        q = request.values['q']
        session_em = session['email']
        if q is not "" and q is not None:
            post = Post.search(q)
            return render_template('posts.html',
                                   error=str(len(post)) + " Results for " + str(q),
                                   posts=post,
                                   session_email=session_em)
        return render_template('posts.html',
                               error="You need to write something in there.",
                               posts=Post.get_posts(),
                               session_email=session_em)
    except KeyError:
        render_template('posts.html',
                        error="",
                        posts=Post.get_posts(),
                        session_email=None)


if __name__ == '__main__':
    app.run(port=1996)
