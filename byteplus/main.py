import base64
import hashlib
import random
import time


import streamlit as st
from io import BytesIO
import os
import openai
from openai import AzureOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import requests
from PIL import Image
import json
import re

ak = "71848bd4d15711eea9180c42a1d032be"
sk = "7184d972d15711eea9180c42a1d032be"


def save_uploaded_image(uploaded_image, file_path):
    with open(file_path, "wb") as f:
        f.write(uploaded_image.getbuffer())


def create_client_for_vision():
    api_base = os.getenv("AZURE_AILAB_ENDPOINT")
    api_key = os.getenv("AILAB_API_KEY")

    deployment_name = os.getenv("AZURE_AILAB_VISION_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_AILAB_VISION_VERSION_NAME")

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{api_base}/openai/deployments/{deployment_name}"
    )
    return client, deployment_name


def create_client(_type):
    if _type == "OpenAI":
        _client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    elif _type == "AzureOpenAI":
        _client = AzureOpenAI(api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                              azure_endpoint=os.getenv("AZURE_AILAB_ENDPOINT"),
                              api_key=os.environ['AILAB_API_KEY']
                              # not deployed yet to openaitest
                              # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                              # api_key=os.environ['AZURE_OPENAI_API_KEY']
                              )
    return _client


# def generate_text_from_image(_client, _deployment_name, _prompt, max_tokens, _base64_image=None):
#     """
#     GPT-4-VISION
#     """
#
#     _response = _client.chat.completions.create(
#         model=_deployment_name,
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": [
#                 {
#                     "type": "text",
#                     "text": _prompt
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{_base64_image}"
#                     }
#                 }
#             ]}
#         ],
#         max_tokens=max_tokens
#     )
#
#     print(_response)
#
#     return _response

def find_max_number_generated(files_path):
    """
    Finds the latest generated file's id
    """

    files = os.listdir(files_path)

    # Define a regular expression pattern to extract numbers from file names
    pattern = re.compile(r'\d+')
    numbers = []

    for file_name in files:
        matches = pattern.findall(file_name)
        numbers.extend(map(int, matches))

    max_number = 0
    if numbers:
        max_number = max(numbers)
        print(f"The maximum number in the file names is: {max_number}")
    else:
        print("No numbers found in the file names.")
    return max_number


def show_image_after_generation(result, _type):
    image_dir = os.path.join(os.curdir, 'images')

    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    new_image_no = find_max_number_generated(image_dir) + 1
    # new image
    image_path_and_name = os.path.join(image_dir, 'generated_image' + str(new_image_no) + '.png')

    # Retrieve the generated image
    if _type == "openai":
        image_url = result.data[0].url
    elif _type == "byteplus":
        # resp_dict = json.loads(result.content)
        # image_data = base64.b64decode(
        #     resp_dict["data"]["image"])
        resp_dict = json.loads(result.content)
        image_data = base64.b64decode(
            resp_dict["data"]["image"])
    else:
        json_response = json.loads(result.model_dump_json())
        image_url = json_response["data"][0]["url"]  # extract image URL from response

    # generated_image = requests.get(image_url).content  # download the image
    with open(image_path_and_name, "wb") as image_file:
        image_file.write(image_data)

    return image_path_and_name


def gen_sign(nonce, security_key, timestamp):
    keys = [str(nonce), str(security_key), str(timestamp)]
    keys.sort()
    keystr = ''.join(keys).encode('utf-8')
    signature = hashlib.sha1(keystr).hexdigest()
    return signature.lower()


def comic_potrait(base64_image_input):
    post_url = "https://cv-api.byteintlapi.com/api/image-process/v1/cartoons"
    nonce = random.randint(0, (1 << 31) - 1)
    security_key = sk
    timestamp = int(time.time())
    sign = gen_sign(nonce, security_key, timestamp)
    form = dict()

    params = {
        "api_key": ak,
        "timestamp": str(timestamp),
        "nonce": str(nonce),
        "sign": sign,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    formData = {
        "image_base64": base64_image_input,
        "cartoon_type": "classic_cartoon",
        "rotation": 0,
    }

    resp = requests.post(url=post_url, params=params,
                         headers=headers, data=formData)

    return resp


def generate_avatar_api():
    """
    Front end with streamlit for  image to text
    2 steps:
        - input image via GPT4V into text
        - input text via DALL-E-3 into new avatar image
    """
    st.title("Profile Avatar")

    st.header("input image")
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        base64_image = base64.b64encode(uploaded_image.getvalue()).decode('utf-8')

    st.write("\n")
    if st.button("Generate Avatar"):
        response = comic_potrait(base64_image)
        image_path = show_image_after_generation(response, "byteplus")
        if response:
            st.header("Generated Profile Describer")
            st.image(image_path, use_column_width=True)

    exit_button = st.button("Exit")
    if exit_button:
        st.stop()


if __name__ == "__main__":
    generate_avatar_api()
