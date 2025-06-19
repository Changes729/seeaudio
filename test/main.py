from deepface import DeepFace
import cv2
import os
import time
import click
import requests

from acestep.pipeline_ace_step import ACEStepPipeline
from acestep.data_sampler import DataSampler


IDLE = False
PLAYING = True
file_url = "http://192.168.3.113:1234"  # Local server URL for audio files
base_url = "http://192.168.3.111"       # ESP32 IP address
url_capture =  base_url + "/capture"
url_is_play = base_url + "/audio_playing"
url_play_audio = base_url + "/play"
image_path = "captured_image.jpg"
audio_path = "/music/test.wav"

os.environ["CUDA_VISIBLE_DEVICES"] = str(0)

model_demo = ACEStepPipeline(
    checkpoint_dir="./ACE-Step/ace_step",
    dtype="bfloat16",
    torch_compile=False,
    cpu_offload=False,
    overlapped_decode=False
)

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

def readImgAndToMusic(image_path, output_path, custom_prompt = ""):
    frame = cv2.imread(image_path)

    # 检查图片是否成功加载
    if frame is None:
        print(f"错误：无法加载图片 {image_path}")
    else:
        # 分析情绪
        results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        result = results[0]

        is_happy = result['dominant_emotion'] == "happy"
        if not is_happy:
            return None
        happy_score = result['emotion']['happy']
        happy_desc = "Content"
        if happy_score <= 50:
            happy_desc = "Content"
        elif happy_score < 60:
            happy_desc = "Pleased"
        elif happy_score < 65:
            happy_desc = "Happy"
        elif happy_score < 70:
            happy_desc = "Delighted"
        elif happy_score < 75:
            happy_desc = "Excited"
        elif happy_score < 80:
            happy_desc = "Joyful"
        elif happy_score < 85:
            happy_desc = "Ecstatic"
        elif happy_score < 90:
            happy_desc = "Elated"
        elif happy_score < 95:
            happy_desc = "Blissful"
        else:
            happy_desc = "Euphoric"

        print("happy level", happy_desc)

        import random
        seed = random.randint(10, 100000)

        model_demo(
            audio_duration=5,
            prompt=happy_desc + custom_prompt,
            lyrics="[inst]",
            infer_step=27,
            guidance_scale=15,
            scheduler_type="euler",
            cfg_type="apg",
            omega_scale=10,
            manual_seeds=seed,
            guidance_interval=0.5,
            guidance_interval_decay=0,
            min_guidance_scale=3,
            use_erg_tag=True,
            use_erg_lyric=False,
            use_erg_diffusion=True,
            oss_steps=None,
            guidance_scale_text=0,
            guidance_scale_lyric=0,
            save_path=output_path,
        )

while True:
    waiting_audio_until(IDLE)
    response = requests.get(url_capture)
    if response.status_code == 200:
        save_image(response._content)
        print("Image captured successfully.")
        with open(image_path, 'wb') as f:
            f.write(response.content)
        readImgAndToMusic(image_path, audio_path, ",pop music")
        waiting_send_audio()
    else:
        print("Failed to capture image. Status code:", response.status_code)
