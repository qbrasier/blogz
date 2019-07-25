from flask import Flask, request, render_template, redirect, session, url_for
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
#app.config['SERVER_NAME']='192.168.1.146:5000'
app.secret_key = b'p8uasdhaosnd98sayd97yahs23>>>>><.'

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship("Blog", backref="user")

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    content = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
   
    def __init__(self, title, content, user):  
        self.content = content
        self.title = title
        self.user_id = user

@app.before_request
def require_login():
    allowed_routes = ['loginForm', 'signupForm', 'blogs', 'homepage', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
@app.route("/")
@app.route("/index")
def homepage():
    x = User.query.all() 
    #template = env.get_template("index.html")
    #return template.render(users=x)
    return render_template("index.html", users=x)

@app.route("/blog", methods = ["GET"])
def blogs():
    bID = request.args.get('id')
    uID = request.args.get('user')
    if bID == None and uID == None:
        x = Blog.query.all() 
        for i in x:
            print(i)
        return render_template("blogs_page.html", blogs = x)
    if bID != None:
        #render a single blog like before
        blog = Blog.query.get(bID)
        username = blog.user.username
        userID = blog.user.id
        print('username should be '+username)
        return render_template("blog_page.html", blog=blog, userID=userID) 

    if uID != None:
        #render all blogs by this user
        #DONE: make this work
        print("the user id should be " +uID)
        x = Blog.query.filter_by(user_id=uID).all()
        y = User.query.get(uID)
        print(y.username)
        return render_template("singleUser.html", blogs = x, username=y.username )

    print("Something strange happened.")
    return "something strange happened." 
    

    #return "here we have blogs. the blog id you are trying to see is " + str(id)

@app.route("/newpost", methods = ['GET','POST'])
def showBlogForm():
    template = env.get_template("write_blog.html")
    if request.method == 'POST':
        if (session['username'] == None):
            return redirect('/login')
        if (len(request.form['title']) > 20):
            return render_template("write_blog.html", error="title too long.")
        if (len(request.form['title']) < 1):
            return render_template("write_blog.html", error="title too short.")
        if (len(request.form['content']) > 200):
            return render_template("write_blog.html", error="blog post too long.")
        if (len(request.form['content']) < 1):
            return render_template("write_blog.html", error="blog post too short.")
        title = request.form['title']
        content = request.form['content']
        new_blog = Blog(title, content, User.query.filter_by(username=session['username']).first().id )
        db.session.add(new_blog)
        db.session.commit()
        return redirect("/blog?id="+str(new_blog.id))
    return render_template("write_blog.html")

@app.route("/signup", methods=['GET','POST'])
def signupForm():
    username_error = ''
    password_error1 = ''
    password_error2 = ''
    email_error = ''

    template = env.get_template('signup.html')
    # here we are checking to make sure the user input includes all required fields.
    
    if(request.method == 'POST'):
        info = request.form
        
        if (info['username'] == ''):
            username_error="You are missing a username."
        if (info['password1'] == ''):    
            password_error1="You are missing your password."
        if (info['password2'] == ''): 
            password_error2="You are missing your password."


        if (" " in info['username']):
            username_error="Make sure there are no spaces in your username."
        if (" " in info['password1']):    
            password_error1="Make sure there are no spaces in your password."
        if (" " in info['password2']): 
            password_error2="Make sure there are no spaces in your password."
        #if (" " in info['email']):
        #    email_error="Make sure there are no spaces in your email"
        # here we are making sure that the password confirmation matches. from here on we can
        # use validation for only password1 since we know that password1 and password2 match.
        if(not info['password1'] == info['password2']):
            password_error2='Your passwords do not match.'

        # username and password length validation
        if(len(info['username']) > 20):
            username_error="Your username is too long. Please make sure it is between 3 and 20 characters in length."
        if(len(info['username']) < 3):
            username_error="Your username is too short. Please make sure it is between 3 and 20 characters in length." 
        if(len(info['password1']) > 20):
            password_error1="Your password is too long. Please make sure it is between 3 and 20 characters in length."
        if(len(info['password1']) < 3):
            password_error1="Your password is too short. Please make sure it is between 3 and 20 characters in length." 

        # here we are making sure that the password confirmation matches. from here on we can
        # use validation for only password1 since we know that password1 and password2 match.
        if(not info['password1'] == info['password2']):
            password_error2='Your passwords do not match.'

        # email validation
        #if not info['email'] == '':
        #    if (not info['email'].count('@') == 1) or (not info['email'].count('.') == 1):
        #        email_error="Your email is formatted invalidly." 
        if(len(username_error)==0 and len(password_error1)==0 and len(password_error2)==0 and len(email_error)==0):
            #DONE: add check to see if username is already registered
            if (User.query.filter_by(username=info['username']).first() == None):
                new_user = User(info['username'],info['password1'])
                db.session.add(new_user)
                db.session.commit()
                session['username'] = info['username']
                print('logging user in')
                return redirect('/newpost')
                #TODO: this needs to be changed later to a welcome page
            else:
                username_error="This username is already taken."
        
        return render_template("signup.html", username_error=username_error,password_error1=password_error1,password_error2=password_error2,
            email_error=email_error, username=info['username'])
    else:    
        return render_template("signup.html")

@app.route("/login", methods=['GET','POST'])
def loginForm():
    template = env.get_template("login.html")
    if request.method == 'GET':
        #print
        return render_template("login.html")
    if request.method == 'POST':
        info = request.form
        print('username:' + info['username'])
        if info['username'] == None or info['username'] == '':
            return render_template("login.html", username_error='You need to enter a username')
        if User.query.filter_by(username=info['username']).first():
            print('this user exists')
            if info['password'] == User.query.filter_by(username=info['username']).first().password:
                session['username'] = info['username']
                print('logging user in')
                return redirect('/newpost')
            else:
                return render_template("login.html", password_error="Invalid password.")
        else:
            print('this user does not exist')
            return render_template("login.html", username_error="This user does not exist.")
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('username', None)
    return redirect('/blog')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
