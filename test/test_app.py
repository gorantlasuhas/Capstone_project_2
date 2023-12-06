import os
import requests
import pytest
from selenium import webdriver

# Assuming your Flask app runs on port 5000
BASE_URL = 'http://localhost:5000'
UPLOAD_FOLDER = 'D:/csp2/yolov8vehicle-Copy2.1/uploads'  # Replace with the correct path

def test_app_running():
    response = requests.get(BASE_URL)
    assert response.status_code == 200

def test_file_upload():
    # Provide the correct path to the test video file
    video_path = os.path.join(UPLOAD_FOLDER, 'test_video.mp4')
    files = {'video': open(video_path, 'rb')}
    response = requests.post(f'{BASE_URL}/process_video', files=files)
    assert response.status_code == 200
    assert 'Success' in response.text

def test_example_unit_1():
    assert 1 + 1 == 2

def test_example_unit_2():
    assert "hello".upper() == "HELLO"

# Selenium test
@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_selenium(browser):
    browser.get(BASE_URL)  # Assuming your React app runs on port 3000
    assert "React App" in browser.title
