import pytest
from test_login import get_csrf_token

def test_feedback(client):
    csrf_token = get_csrf_token(client, '/feedback')
    response = client.post('/feedback', data=dict(
        message = "Test Feedback",
        csrf_token = csrf_token
        ), follow_redirects=True)
    assert b'form' not in response.data
    assert b'Feedback submitted' in response.data
