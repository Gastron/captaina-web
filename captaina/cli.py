import click
from flask.cli import AppGroup, with_appcontext

user_cli = AppGroup('user')
lesson_cli = AppGroup('lesson')

def register_cli(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(lesson_cli)


### user ###
@user_cli.command('create')
@click.argument('username')
@click.argument('plaintext-password')
@click.option('--teacher', is_flag=True)
def create_user(username, plaintext_password, teacher):
    from .models import create_user
    try:
        create_user(username, plaintext_password, teacher)
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


### lesson ###
@lesson_cli.command('create')
@click.argument('name')
@click.argument('prompts-file')
def create_lesson(name, prompts_file):
    from .models import Prompt, Lesson, create_lesson_with_safe_url_id
    with open(prompts_file) as fi:
        lesson = create_lesson_with_safe_url_id(name)
        prompts = []
        for graph_id, *words in [line.strip().split() for line in fi]:
            prompt = Prompt()
            prompt.graph_id = graph_id
            prompt.text = " ".join(words)
            prompt.save()
            prompts.append(prompt)
        lesson.prompts = prompts
    lesson.save()
             
