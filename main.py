from flask import Flask, render_template, request, redirect, url_for, make_response
from models import User, db
import random

app = Flask(__name__)
db.create_all()


@app.route("/")
def index():
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()

    message = request.args.get('message')
    response = make_response(render_template("index.html", user=user, message=message))

    if user and not user.secret_number:
        user.secret_number = random.randint(1, 30)
        db.session.commit()

    return response


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")

    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email)
        db.add(user)
        db.commit()

    response = make_response(redirect(url_for('index')))
    response.set_cookie("email", email)

    return response


def get_message(guess, secret_number):
    message = ''

    if guess == secret_number:
        message = "Correct! The secret number is {0}".format(str(secret_number))
    elif guess > secret_number:
        message = "Your guess is not correct... try something smaller."
    elif guess < secret_number:
        message = "Your guess is not correct... try something bigger."

    return message


@app.route("/secret", methods=["POST"])
def secret():
    guess = int(request.form.get("guess"))

    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()

    response = make_response(
        redirect(url_for(
            'index',
            message=get_message(guess=guess, secret_number=user.secret_number))
        )
    )

    if guess == user.secret_number:
        user.secret_number = random.randint(1, 30)
        db.session.commit()

    return response


if __name__ == '__main__':
    app.run()
