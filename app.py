from flask import Flask, render_template, request, redirect, abort, jsonify, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import random
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.secret_key = 'supersecretkeyhere0123456987'

db = SQLAlchemy(app)


# database setup
class DataSchema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(25), nullable=False, unique=True)
    url = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Url {self.slug} Created"

# validator


def validateSlug(strObj):
    pattern = re.compile('[\w\-]')
    if(re.match(pattern, strObj) is None):
        return False
    return True


# def validateUrl(urlObj):
#     self.urlObj = urlObj
#     pattern = re.compile(
#         '((?:https?://|s?ftps?://|file://|javascript:|data:|www\d{0,3}[.])[\w().=/;,#:@?&~*+!$%\'{}-]+)', re.UNICODE)
#     if(re.match(pattern, self.urlObj) is None):
#         return False
#     return True


# routes
@app.route("/?res=error", methods=["GET"])
def form_error():
    if session["error"] is not None:
        error = session["error"]
    return render_template("index.html", error=error)


@app.route("/?res=success", methods=["GET"])
def form_success():
    if session["new_url"] is not None:
        data = session["new_url"]
    return render_template("index.html", data=data)

# creates a new url with slug/alias


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        request_slug = request.form["slug"]
        request_url = request.form["url"]

        if not request_url or request_url == "":
            session["error"] = "please provide a valid url 😢"
            return redirect(url_for('form_error'))

        # TODO: validate request url

        if not request_slug or request_slug == "":
            num = random.randint(1, 1000000)
            request_slug = f"default-{num}"
        else:
            if not validateSlug(request_slug):
                session["error"] = "please provide a valid (alpha-numeric) slug, eg. default-125 😢"
                return redirect(url_for('form_error'))
        checkSlug = DataSchema.query.filter_by(slug=request_slug).first()
        if checkSlug is not None:
            session["error"] = "sorry slug is already in use 😢"
            return redirect(url_for('form_error'))

        session.clear()
        new_url = DataSchema(slug=request_slug, url=request_url)
        print(new_url)
        db.session.add(new_url)
        db.session.commit()
        data = {}
        data["id"] = new_url.id
        data["slug"] = new_url.slug
        data["url"] = new_url.url
        session["new_url"] = data
        return redirect(url_for('form_success'))


# index page


@app.route("/links", methods=["GET"])
def links():
    all_urls = DataSchema.query.order_by(desc(DataSchema.id)).all()
    links = DataSchema.query.count()
    return render_template("links.html", urls=all_urls, links=links)


# resolve url from slug and redirect
@app.route("/<string:slug>")
def url_resolve(slug):
    try:
        res = DataSchema.query.filter_by(slug=slug).first()
        if res is None:
            return redirect(url_for("index"))
        return redirect(res.url)
    except:
        # TODO: solve multiple redirection issues
        abort(404)


if __name__ == "__main__":
    app.run(debug=True)
