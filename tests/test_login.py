import pytest
import re
import time

def get_csrf_token(client, uri):
    form = client.get(uri)
    match = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([^"]*)"', form.data)
    return match.group(2).decode('utf-8')

def post_with_csrf(client, uri, data):
    data['csrf_token'] = get_csrf_token(client, uri)
    response = client.post(uri, 
            data=data,
            follow_redirects=True)
    if b'CSRF token is invalid' not in response.data:
        return response
    else:
        raise RuntimeError("CSRF validation didn't succeed")

def login(client, username, password):
    return post_with_csrf(client, '/login', 
            data=dict(
        username=username,
        password=password))

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_login(client, uuid):
    from captaina.models import create_user
    create_user(uuid, 'password')
    response = login(client, uuid, 'password')
    assert b'You were logged in' in response.data
    logout(client)

    response = login(client, uuid, 'hunter2')
    assert b'Invalid password' in response.data

    response = login(client, 'unknown', 'pass')
    assert b'Invalid username' in response.data

def test_login_required(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in' in response.data
