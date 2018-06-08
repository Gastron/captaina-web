import click
from flask.cli import AppGroup, with_appcontext

user_cli = AppGroup('user')

def register_cli(app):
    app.cli.add_command(user_cli)

@user_cli.command('create')
@click.argument('username')
@click.argument('plaintext-password')
def create_user(username, plaintext_password):
    from .models import create_user
    try:
        create_user(username, plaintext_password)
    except ValueError as err:
        e = click.ClickException(str(err))
        e.exit_code = 1
        raise e

@user_cli.command('change-password')
@click.argument('username')
@click.argument('new-plaintext-password')
def change_password(username, new_plaintext_password):
    from .models import change_password
    try:
        change_password(username, new_plaintext_password)
    except ValueError as err:
        e = click.ClickException(str(err))
        e.exit_code = 1
        raise e
