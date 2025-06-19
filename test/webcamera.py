import requests
import time

def save_image(image_data):
    """
    Save the captured image data to a file.
    :param image_data: The binary content of the image.
    """
    with open('captured_image.jpg', 'wb') as f:
        f.write(image_data)
    print("Image saved as 'captured_image.jpg'.")

def waiting_audio_until(playing):
    """
    Wait until the audio is ready to be played.
    :param ready: A boolean indicating whether the audio is ready.
    """
    while True:
        response = requests.get(url_is_play)
        if response.status_code == 200:
            pass_condition = "true" if playing else "false"
            if response.text == pass_condition:
                print("Audio is ready to be played.")
                break
            else:
                print("Waiting for audio to be ready...")
        else:
            print("Failed to check audio status. Status code:", response.status_code)
        time.sleep(2)
    time.sleep(2)

def  waiting_send_audio():
    while True:
        waiting_audio_until(IDLE)
        print("Audio can be played, sending audio...")
        response = requests.post(url_play_audio, data=file_url + audio_path)
        if response.status_code == 200:
            print("Audio sent successfully.")
            # waiting_audio_until(PLAYING)
            time.sleep(3)
        else:
            print("Failed to send audio. Status code:", response.status_code)

file_url = "http://192.168.3.113:1234"
base_url = "http://192.168.3.111"
url_capture =  base_url + "/capture"
url_is_play = base_url + "/audio_playing"
url_play_audio = base_url + "/play"
image_path = "captured_image.jpg"
audio_path = "/pianos-by-jtwayne-7-174717.mp3"

IDLE = False
PLAYING = True

while True:
    waiting_audio_until(IDLE)
    response = requests.get(url_capture)
    if response.status_code == 200:
        save_image(response._content)
        print("Image captured successfully.")
        with open(image_path, 'wb') as f:
            f.write(response.content)
        waiting_send_audio()
    else:
        print("Failed to capture image. Status code:", response.status_code)
