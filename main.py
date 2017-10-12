from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title,body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST','GET'])
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html',blogs=blogs)



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    error = ""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['blogpost']
        if title and body :
            new_post = Blog(title,body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')

        else:
             error = "Please enter a title and body both fields are mandatory for a valid blog post !!!"
    return render_template('newpost.html',title = "New Post",error=error)


if __name__ == '__main__':
    app.run()