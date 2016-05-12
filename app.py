#!/usr/bin/python
import glob
import itertools

import os

home = '/advances'
os.environ["SCRIPT_NAME"] = home
os.environ["REAL_SCRIPT_NAME"] = home

import web
from web import form

DB_NAME = "db.db"
DB_TABLE = "registration"
DB_COLUMNS = ("title", 'surname', 'name', 'institute', 'city', 'country', 'email', 'ptitle', 'pabstract', 'ptype', 'pcomment')

db = web.db.database(dbn='sqlite', db=DB_NAME)

render = web.template.render('templates')
vpass = form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
vemail = form.regexp(r".*@.*", "must be a valid email address")
botmsg = "Please enter any last name of an organizer."


def check_bot(i):
    return i["botcheck"] in ("Abel", "Feudel", "Grassberger", "Politi", "Rosenblum")


def check_submission(i, key):
    if i["ptype"] == "None":
        return True
    else:
        return bool(i[key])


register_form = form.Form(
    form.Dropdown("title", ('Mr.', 'Mrs.', 'Dr.', 'Prof.'), description="Title"),
    form.Textbox("surname", form.notnull, description="Surname"),
    form.Textbox("name", form.notnull, description="Name"),
    form.Textbox("institute", form.notnull, description="Institute"),
    form.Textbox("city", form.notnull, description="City"),
    form.Textbox("country", form.notnull, description="Country"),
    form.Textbox("email", vemail, description="E-Mail"),
    form.Radio("ptype", ("Poster", "None"), form.notnull, description="Type"),
    form.Textarea("ptitle", description="Title", cols=70, rows=1),
    form.Textarea("pabstract", description="Abstract", cols=70, rows=20),
    form.Textarea("pcomment", description="Comment", cols=70, rows=3),
    form.Textbox("botcheck", value=botmsg, description="Botcheck", size=len(botmsg)),
    form.Button("submit", type="submit", description="Register"),
    validators=[form.Validator("Poster title is missing.", lambda i: check_submission(i, "ptitle")),
                form.Validator("Poster abstract is missing.", lambda i: check_submission(i, "pabstract")),
                form.Validator("Botcheck failed.", check_bot)]
)


class Registration:
    def GET(self):
        f = register_form()
        return render.registration(f, None)

    def POST(self):
        f = register_form()
        if not f.validates():
            msg = "Poster information incomplete!"
            return render.registration(f, msg)
        else:
            values = dict((k, f.value[k]) for k in DB_COLUMNS)
            with db.transaction():
                db.insert(DB_TABLE, **values)

            email_body = "{title} {surname} {name} from {institute} registered for the conference.".format(**values)
            #web.sendmail('advances', ['mros@uni-potsdam.de', 'mquade@uni-potsdam.de'], 'New registration for advances', email_body)
            msg = "Registration successful"
            return render.registration(f, msg)

class StaticSite:
    def GET(self, name):
        name = name[:-1]
        return render.__getattr__(name)()

class Root:
    def GET(self):
        return render.index()


urls = (
        "/registration/", Registration,
        "/(.*/)", StaticSite,
        "/", Root
    )

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
