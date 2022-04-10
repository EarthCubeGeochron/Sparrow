from click import echo, style, prompt, secho
from ..database.models import User


def _create_user(db, username, password):
    user = User(username=username)
    db.session.add(user)
    user = _reset_password(db, user, password)
    return user


def _reset_password(db, user, password):
    user.set_password(password)
    db.session.add(user)
    assert user.is_correct_password(password)
    return user


def list_users(db):
    users = db.session.query(User).all()
    for user in users:
        print(user.username)


def reset_password(db, username):
    user = db.session.query(User).filter_by(username=username).first()
    if user is None:
        secho(f"No user with name {username} exists.", fg="red")
        return
    password = prompt("Create a password", hide_input=True, confirmation_prompt=True)
    _reset_password(db, user, password)
    db.session.commit()


def _format_username(username):
    return "Username {}".format(style(username, fg="cyan", bold=True))


def create_user(db):
    username = prompt("Enter the desired username")
    while db.session.query(User).get(username) is not None:
        username = prompt(
            _format_username(username) + " is already taken. Choose another"
        )
    echo(_format_username(username) + " is available!")

    password = prompt("Create a password", hide_input=True, confirmation_prompt=True)
    _create_user(db, username, password)
    db.session.commit()
    echo("Successfully created user and hashed password!")
