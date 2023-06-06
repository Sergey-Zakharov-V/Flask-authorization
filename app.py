import os
import sqlite3
from misc import FDataBase, UserLogin
from flask import Flask, render_template, url_for, request, flash, session, redirect, url_for, abort, g, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Конфигурация
SECRET_KEY = "fghjkf2sddfghjsdaj3mlkam2sdjorikte"
DEBUG = True
USE_RELOADER = True
DATABASE = "sql_api/users.db"

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "misc/sql_main/users.db")))
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Авторизуйтесь чтобы видеть закрытый контент"
login_manager.login_message_category = "error"


def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    db.cursor().execute("""CREATE TABLE IF NOT EXISTS users(
    login TEXT,
    password TEXT,
    photo BLOB,
    rule INTEGER DEFAULT 0)""")
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, "link.db"):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link.db"):
        g.link_db.close()


@login_manager.user_loader
def load_user(user_login):
    return UserLogin().fromDB(user_login, dbase)

@app.route("/")
@app.route("/home")
def index():
    return render_template("welcome.html", title="Главная страница")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("account", user_id=current_user.get_id()))
    if request.method == "POST":
        if request.form['login'] and request.form["password"]:
            user_login = dbase.getUser(request.form['login'])
            if user_login:
                if request.form['login'] == user_login[0] and check_password_hash(user_login[1], request.form['password']):
                    session.permanent = True
                    session["admin"] = user_login[2]
                    userlogin = UserLogin().create(user_login)
                    login_user(userlogin)
                    return redirect(request.args.get("next") or url_for("account", title="Авторизация", user_id=current_user.get_id()))
                flash("Неверный логин или пароль!", "error")
            else:
                flash("Неверный логин или пароль!", "error")
        else:
            flash("Неверный логин или пароль!", "error")
    return render_template("login.html", title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("account", user_id=current_user.get_id()))
    if request.method == "POST":
        login_ = request.form['login']
        password_ = generate_password_hash(request.form['password'])
        dbase.register_account(login_, password_)
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/admin", methods=["POST", "GET"])
@login_required
def admin_menu():
    return render_template("adminmenu.html", admin_name=current_user.get_id(), users=dbase.getAllUser())


@app.route("/ban/<int:id>", methods=["POST", "GET"])
def ban(id):
    if "POST" in request.method:
        dbase.delete_user(id)
    return redirect(url_for("admin_menu"))


@app.route("/account/<path:user_id>")
def account(user_id):
    if current_user.is_authenticated:
        return render_template("account.html", user_id=user_id, user_login=current_user.get_id())
    else:
        abort(401)


@app.route("/exit", methods=["POST", "GET"])
def exit_():
    logout_user()
    session.clear()
    return redirect(url_for("index"))


@app.route("/news/<int:values>")
@login_required
def news(values):
    return f"<h1>News {values}</h1>"


@app.errorhandler(404)
def page_not_found(error):
    return "<h1>Ошибка 404</h1>", 404


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="192.168.0.167")
