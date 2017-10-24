from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:done@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key ="#secretKEY"


def valid_username(username):
    if ' ' in username or len(username) == 0 or len(username)<3 or len(username)>20:
        return False
    return True   

def valid_password(password):
    if password.find(' ') != -1 or len(password) == 0 or len(password)<3 or len(password)>20:
        return False
    return True  

@app.before_request
def require_login():
    allowed_routes = ['login','signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session :
        return redirect('/login')
 

class User(db.Model):
    id = db.Column(db.Integer,primary_key =True)
    username = db.Column(db.String(120),unique =True)
    password  = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref ='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title,body, owner):
        self.title = title
        self.body = body
        self.owner = owner


@app.route('/login', methods =['POST','GET'])
def login():
    if request.method =='POST':
        username =request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in","success")
            return redirect('/blog/newpost')
        else:
            flash("User password incorrect or user does not exist","error")

    return render_template('login.html')  

@app.route('/signup',methods =['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #validate user data
        if valid_username(username) and valid_password(password)and password ==verify :
     
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user= User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("user registered","success")
                return redirect('/login')
            else:
                #TODO explain why log in failed
                flash("User already exists ","error")
                return redirect('/signup')
                
        else:
            if not valid_username(username):
                username_error = "That is not a valid username"
            else:
                username_error = ""
            if not valid_password(password):
                password_error= "That is not a valid password"    
            else:
                password_error =""
            if not password == verify  :
                verify_error = "passwords dont match"
            else:
                verify_error = ""    
            return render_template('signup.html',username_error = username_error,
                                                password_error = password_error,
                                                verify_error = verify_error,
                                                username=username)
    return render_template('signup.html')

@app.route('/logout')
def logout():
    flash(session['username'] + ' logged out',"success")
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():

    users = User.query.all()
    return render_template('index.html',users = users)


@app.route('/blog', methods=['POST','GET'])
def blog():

     username = request.args.get('user') 
     if username:

         user = User.query.filter_by(username=username).first()
         blogs = Blog.query.filter_by(owner_id=user.id)
         return render_template('userposts.html',blogs =blogs,username = username)
  
     id = request.args.get('id')
     if id:
         blog = Blog.query.get(id)
         return render_template('viewpost.html',blog =blog,username = blog.owner.username)    

     blogs = Blog.query.all()
     return render_template('blog.html',blogs=blogs)


@app.route('/blog/newpost', methods=['POST', 'GET'])
def newpost():
    error = ""
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['blogpost']
        if title and body :
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(title,body,owner)
            db.session.add(new_blog)
            db.session.commit()
            page = str(new_blog.id)
            return redirect('/blog?id='+page)

        else:
            error = "Please enter a title and body both fields are mandatory for a valid blog post !!!"
   
    return render_template('newpost.html',title = "New Post",error=error)


if __name__ == '__main__':
    app.run()