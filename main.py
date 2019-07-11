from flask import Flask, request, render_template
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

env = Environment(
    loader=FileSystemLoader('./Templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

db = SQLAlchemy(app)

class Blog(db.Model):
    #changed this so need to delete databse and remake
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    content = db.Column(db.String(255))
   

    def __init__(self, content, title):    # apparently i need to change this to accept content and title becuase
        self.content = content
        self.title = title



@app.route("/")
def homepage():
    return "hi"

@app.route("/blog", methods = ['POST'])
def blogs():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_blog = Blog(title, content)
        db.session.add(new_blog)
        db.session.commit()

    return "here we have blogs"

@app.route("/newpost")
def showBlogForm():
    template = env.get_template("write_blog.html")
    return template.render()



if __name__ == '__main__':
    app.run()
