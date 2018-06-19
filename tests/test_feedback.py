import pytest
from test_login import post_with_csrf 

def test_feedback(client):
    response = post_with_csrf(client, '/feedback', 
            data=dict(
        message = "Test Feedback",
        ))
    assert b'form' not in response.data
    assert b'Feedback submitted' in response.data
