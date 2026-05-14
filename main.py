import os

from flask import Flask, flash, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

from models import db, User, Menu, Reservation, Order, OrderItem
from forms import SignUpForm, SignInForm


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_URI")
app.secret_key = os.getenv("SECRET_KEY")
db.init_app(app)
login_manager = LoginManager(app)


# with app.app_context():
#     db.drop_all()
#     db.create_all()



@login_manager.user_loader
def user_loader(user_id):
    return User.query.filter_by(id=int(user_id)).first()

@app.route("/sign_up/", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash("Користувач з таким логіном вже існує.")
            return redirect(url_for("sign_up"))
        
        user = User(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data or None,
            fullname=form.fullname.data or None
        )
        db.session.add(user)
        db.session.commit()
        flash("Реєстрація успішна.")
        return redirect(url_for("sign_in"))
    return render_template("sign_up.html", form=form)


@app.route("/sign_in/", methods=["GET", "POST"])
def sign_in():
    form = SignInForm()

    if form.validate_on_submit():
        user: User = User.query.filter_by(username=form.username.data).first()
        if not user and user.is_password_verify(form.password.data) and user.is_active:
            login_user(user)
            flash("Ви успішно увійшли.")
            return redirect(url_for("index"))
        
        flash("Невірний логін або пароль.")
        return redirect(url_for("sign_in"))
    return render_template("sign_in.html", form=form)

        
@app.get("/logout/")
@login_required
def logout():
    logout_user()
    flash("Дякую за використання нашого сервісу.")
    return redirect(url_for("sign_in"))


@app.get("/")
@login_required
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
