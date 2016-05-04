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
                form.Validator("Poster abstract is missing.", lambda i: check_submission(i, "abstract")),
                form.Validator("Botcheck failed.", check_bot)]
)


class Register:
    def GET(self):
        f = register_form()
        return render.register(f)

    def POST(self):
        f = register_form()
        if not f.validates():
            return render.register(f)
        else:
            values = {k: f.value[k] for k in DB_COLUMNS}
            with db.transaction():
                db.insert(DB_TABLE, **values)
            return web.seeother("/")


urls = ("/", Register)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
