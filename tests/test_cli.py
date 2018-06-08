import click

def test_create_user(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['user', 'create', 'user', 'pass'])
    assert result.exit_code == 0 

    result = runner.invoke(args=['user', 'create', 'user', 'pass'])
    assert result.exit_code == 1

    result = runner.invoke(args=['user', 'create', 'user2'])
    assert result.exit_code == 2

def test_change_password(app):
    runner = app.test_cli_runner()
    runner.invoke(args=['user', 'create', 'user', 'pass'])
    result = runner.invoke(args=['user', 'change-password', 'user', 'hunter2'])
    assert result.exit_code == 0 

    result = runner.invoke(args=['user', 'change-password', 'user2', 'hunter2'])
    assert result.exit_code == 1
