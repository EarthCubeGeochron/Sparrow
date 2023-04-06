import click
from click import echo, secho, style, prompt
from sqlalchemy.exc import IntegrityError
from sparrow.database.models import User


def _create_user(db, username, password, raise_on_error=True):
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        assert user.is_correct_password(password)
        db.session.commit()
        return user
    except IntegrityError:
        db.session.rollback()
        if raise_on_error:
            raise


def create_user(db):
    username = prompt("Enter the desired username")
    name = "Username {}".format(style(username, fg="cyan", bold=True))
    while db.session.query(User).get(username) is not None:
        username = prompt(name + " is already taken. Choose another.")
    echo(name + " is available!")

    password = prompt("Create a password", hide_input=True, confirmation_prompt=True)
    _create_user(db, username, password)
    echo("Successfully created user and hashed password!")
