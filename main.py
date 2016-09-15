import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kws):
        self.response.out.write(*args, **kws)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kws):
        self.write(self.render_str(template, **kws))

class MainPage(Handler):
    def get(self):
        self.redirect('/blog')

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    content = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogPosts(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("blog.html", posts = posts)

class NewPost(Handler):
    def render_newpost(self, title = "", content = "", error = ""):
        self.render("newpost.html", title = title, content = content, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            post = BlogPost(title = title, content = content)
            post.put()
            self.redirect("/blog")
        else:
            error = "we need both a title and some content"
            self.render_newpost(title = title, content = content, error = error)

class ViewPostHandler(Handler):
    def get(self, id):
        post = BlogPost.get_by_id(int(id))
        self.render("post.html", post = post)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPosts),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
