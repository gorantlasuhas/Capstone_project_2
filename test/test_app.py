import requests
import pytest

def test_app_running():
    response = requests.get('http://localhost:5000')
    assert response.status_code == 200

def test_file_upload():
    files = {'video': open('path/to/test_video.mp4', 'rb')}
    response = requests.post('http://localhost:5000/process_video', files=files)
    assert response.status_code == 200
    assert 'Success' in response.text

def test_example_unit_1():
    assert 1 + 1 == 2

def test_example_unit_2():
    assert "hello".upper() == "HELLO"
