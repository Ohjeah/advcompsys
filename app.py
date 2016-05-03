import web
from web import form

import model

DB_NAME = "db.db"

render = web.template.render('templates') # your templates

vpass = form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
vemail = form.regexp(r".*@.*", "must be a valid email address")

def check_bot(i):
    return i["botcheck"] in ("Abel", "Feudel", "Grassberger", "Politi", "Rosenblum")

botmsg = "Please enter any last name of an organiser."

def check_submission(i, key):
    if i["ptype"] == "None":
        return True
    else:
        return bool(i[key])

register_form = form.Form(
    form.Dropdown ("title", ('Mr.', 'Mrs.', 'Dr.', 'Prof.'), description="Title"),
    form.Textbox("surname", form.notnull, description="Surname"),
    form.Textbox("name", form.notnull, description="Name"),
    form.Textbox("institut", form.notnull, description="Institute"),
    form.Textbox("city", form.notnull, description="City"),
    form.Textbox("country", form.notnull, description="Country"),
    form.Textbox("email", vemail, description="E-Mail"),
    form.Radio("ptype", ("Poster", "None"), form.notnull, description="Type"),
    form.Textarea("ptitle", description="Title", cols=70, rows=1),
    form.Textarea("pabstract", description="Abstract", cols=70, rows=20),
    form.Textarea("pcomment", description="Comment", cols=70, rows=3),
    form.Textbox("botcheck", value=botmsg, description="Botcheck", size=len(botmsg)),
    form.Button("submit", type="submit", description="Register"),
    validators = [form.Validator("Poster title is missing.", lambda i: check_submission(i, "ptitle")),
                  form.Validator("Poster abstract is missing.", lambda i: check_submission(i, "abstract")),
                  form.Validator("Botcheck failed.", check_bot)]
)

class register:
    def GET(self):
        # do $:f.render() in the template
        f = register_form()
        return render.register(f)

    def POST(self):
        f = register_form()
        if not f.validates():
            return render.register(f)
        else:
            with model.make_connection(DB_NAME) as connection:
                model.dump_registration(f.value, connection)
            return web.seeother("/")


urls = ("/", register)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()