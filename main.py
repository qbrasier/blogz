from flask import Flask, request, render_template, redirect, session
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
   

    def __init__(self, title, content):    # apparently i need to change this to accept content and title becuase
        self.content = content
        self.title = title



@app.route("/")
def homepage():
    return redirect("/blog")

@app.route("/blog", methods = ["GET"])
def blogs():
    id = request.args.get('id')
    if id == None:
        x = Blog.query.all() 
        for i in x:
            print(i)
        return render_template("blogs_page.html", blogs = x)
    
    print("test")
    blog = Blog.query.get(id)
    return render_template("blog_page.html", blog=blog) 
    

    #return "here we have blogs. the blog id you are trying to see is " + str(id)

@app.route("/newpost", methods = ['GET','POST'])
def showBlogForm():
    template = env.get_template("write_blog.html")
    if request.method == 'POST':
        if (len(request.form['title']) > 20):
            return template.render(error="title too long.")
        if (len(request.form['title']) < 1):
            return template.render(error="title too short.")
        if (len(request.form['content']) > 200):
            return template.render(error="blog post too long.")
        if (len(request.form['content']) < 1):
            return template.render(error="blog post too short.")
        title = request.form['title']
        content = request.form['content']
        new_blog = Blog(title, content)
        db.session.add(new_blog)
        db.session.commit()
        return redirect("/blog?id="+str(new_blog.id))

    
    return template.render()



if __name__ == '__main__':
    app.run()
