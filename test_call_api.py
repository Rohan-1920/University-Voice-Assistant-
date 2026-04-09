import pytest
from fastapi.testclient import TestClient
from call_api import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_incoming_call():
    response = client.post("/voice/incoming")
    assert response.status_code == 200
    assert b"<Response>" in response.content
    assert b"university assistant" in response.content


def test_process_valid_speech():
    response = client.post("/voice/process", data={
        "SpeechResult": "What are your office hours?",
        "From": "+1234567890"
    })
    assert response.status_code == 200
    assert b"Monday through Friday" in response.content


def test_process_empty_speech():
    response = client.post("/voice/process", data={
        "SpeechResult": "",
        "From": "+1234567890"
    })
    assert response.status_code == 200
    assert b"didn't catch that" in response.content


def test_process_none_speech():
    response = client.post("/voice/process", data={
        "From": "+1234567890"
    })
    assert response.status_code == 200
    assert b"didn't catch that" in response.content


def test_registration_query():
    response = client.post("/voice/process", data={
        "SpeechResult": "How do I register?",
        "From": "+1234567890"
    })
    assert response.status_code == 200
    assert b"register" in response.content


def test_tuition_query():
    response = client.post("/voice/process", data={
        "SpeechResult": "How much is tuition?",
        "From": "+1234567890"
    })
    assert response.status_code == 200
    assert b"tuition" in response.content


def test_response_speed():
    import time
    start = time.time()
    client.post("/voice/incoming")
    duration = time.time() - start
    assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
