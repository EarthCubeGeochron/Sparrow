import click
from click import echo, secho, style, prompt
from ..models import User

def create_user(db):
    username = prompt("Enter the desired username")
    name = "Username {}".format(style(username, fg="cyan", bold=True))
    while db.session.query(User).get(username) is not None:
        username = prompt(name+" is already taken. Choose another.")
    echo(name+" is available!")

    password = prompt("Create a password",
        hide_input=True, confirmation_prompt=True)

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    echo("Successfully created user and hashed password!")
