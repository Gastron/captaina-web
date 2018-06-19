import click

def test_create_user(app, uuid):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['user', 'create', uuid, 'pass'])
    assert result.exit_code == 0 

    result = runner.invoke(args=['user', 'create', uuid, 'pass'])
    assert result.exit_code == 1

    result = runner.invoke(args=['user', 'create', uuid+"2"])
    assert result.exit_code == 2

def test_change_password(app, uuid):
    runner = app.test_cli_runner()
    runner.invoke(args=['user', 'create', 'user', 'pass'])
    result = runner.invoke(args=['user', 'change-password', 'user', 'hunter2'])
    assert result.exit_code == 0 

    result = runner.invoke(args=['user', 'change-password', 'user2', 'hunter2'])
    assert result.exit_code == 1
