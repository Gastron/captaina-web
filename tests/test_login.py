import pytest
import re

def get_csrf_token(client, uri):
    form = client.get(uri)
    match = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', form.data)
    return match.group(2).decode('utf-8')

def login(client, username, password):
    csrf_token = get_csrf_token(client, '/login')
    return client.post('/login', data=dict(
        username = username,
        password = password,
        csrf_token = csrf_token
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_login(client):
    from captaina.models import create_user
    create_user('user', 'pass')
    response = login(client, 'user', 'pass')
    assert b'You were logged in' in response.data
    logout(client)

    response = login(client, 'user', 'hunter2')
    assert b'Invalid password' in response.data

    response = login(client, 'user2', 'pass')
    assert b'Invalid username' in response.data
