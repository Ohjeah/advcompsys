#!/usr/bin/python
import datetime
import glob
import itertools
import base64
import hashlib
import re
import os

home = '/advances'
os.environ["SCRIPT_NAME"] = home
os.environ["REAL_SCRIPT_NAME"] = home

import web
web.config.debug = False
from web import form


urls = (
        "/login/", "Login",
        "/participants/", "Participants",
        "/registration/", "Registration",
        "/(.*/)", "StaticSite",
        "/", "Root",
    )

app = web.application(urls, globals())

from allowed import LOGINS


DB_NAME = "db.db"
DB_TABLE = "registration"
DB_COLUMNS = ("title", 'surname', 'name', 'institute', 'city', 'country', 'email', 'ptitle', 'pabstract', 'ptype', 'pcomment')

REGISTRATION_DEADLINE = datetime.datetime(year=2016, month=8, day=31, hour=23, minute=59, second=59)

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
    form.Textbox("surname", form.notnull, description="First name"),
    form.Textbox("name", form.notnull, description="Last name"),
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
            if datetime.datetime.now() > REGISTRATION_DEADLINE:
                msg = "Cannot register after deadline."
            else:
                values = dict((k, f.value[k]) for k in DB_COLUMNS)
                with db.transaction():
                    db.insert(DB_TABLE, **values)

                email_body = u"Dear {title} {surname} {name} from {institute}, \n\
you successfully registered for the conference. \n \n\
Kind regards, \n\
The organizers".format(**values)

                web.sendmail('advances', values['email'], 'Successful registration for advances',
                             email_body, cc=['mros@uni-potsdam.de', 'mquade@uni-potsdam.de'])

                msg = "Registration successful"
            return render.registration(f, msg)


class StaticSite:
    def GET(self, name):
        name = name[:-1]
        return render.__getattr__(name)()


class Root:
    def GET(self):
        return render.index()


class Login:
    def GET(self):
        auth = web.ctx.env['HTTP_AUTHORIZATION']
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ','',auth)
            username, password = base64.decodestring(auth).split(':')
            if (username, hashlib.sha512(password).hexdigest()) in LOGINS:
                web.ctx.env['HTTP_AUTHORIZATION'] = auth
                raise web.seeother('/')
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate', 'Basic realm="Auth example"')
            web.ctx.status = '401 Unauthorized'
            return


def no_test_row(row):
    return not any(re.findall(pattern, s) for pattern in patterns for s in row[2:4])


def encode(row, exclude=(8,)):
    return [s.encode('utf-8') for i, s in enumerate(row) if i not in exclude]

def order(entry):
    return [entry[i] for i in DB_COLUMNS]


patterns = re.compile("[Tt]est"), re.compile("[Qq]uade")


class Participants:
    def GET(self):
        if web.ctx.env['HTTP_AUTHORIZATION'] is not None:
            result = db.select(DB_TABLE)
            result = set(map(tuple, map(order, result)))  # filter duplicates, parse entry
            result = map(encode, filter(no_test_row, result)) # remove tests and encode to utf
            result.insert(0, DB_COLUMNS)
            return render.participants(result)

        else:
            raise web.seeother('/login/')


if __name__ == "__main__":
    app.run()
