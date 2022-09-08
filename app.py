from email.mime import image
from urllib import response
import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import numpy as np
import io

st.set_page_config(
    page_title="License Plate Detection",
    page_icon=":oncoming_police_car:",
    initial_sidebar_state="collapsed" )

def sidebar_uri():
    st.sidebar.write("You can use this URI's example:")
    st.sidebar.code("gs://ocr-361804/license_plate_images/plat1.jpg", language="http")
    st.sidebar.code("https://storage.googleapis.com/ocr-361804/license_plate_images/plat2.jpg", language="http")

def sidebar_image():
    st.sidebar.write("You can download this image samples:")
    st.sidebar.download_button(
        label="download image 1",
        data=open("image_sample/plat1.jpg", "rb").read(),
        file_name="plat1.jpg"
    )
    st.sidebar.download_button(
        label="download image 2",
        data=open("image_sample/plat2.jpg", "rb").read(),
        file_name="plat2.jpg"
    )

def get_text():
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = vision.ImageAnnotatorClient(credentials=credentials)

    def get_image_uri(image_uri):
        image = vision.Image()
        image.source.image_uri = image_uri
        return image

    def get_image_upload(image_file_buffer):
        # content =  Image.open(image_file_buffer)
        content = image_file_buffer.getvalue()
        return vision.Image(content=content)
    
    def get_image_picture(picture):
        content = picture.getvalue()
        return vision.Image(content=content)

    if input_type == "Image URI":
        image = get_image_uri(image_uri=image_uri)
    elif input_type == "Image File":
        image = get_image_upload(image_file_buffer=image_file_buffer)
    else:
        image = get_image_picture(picture=picture)

    response = client.text_detection(image=image)
    for text in response.text_annotations:
        st.write("=" * 30)
        st.write(text.description)
        vertices = ['(%s, %s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
        st.write('bounds:', ",".join(vertices))

st.title("License Plate Detection")

input_type = st.radio("Select input", ("Image URI", "Image File", "Take a Picture"), horizontal=True)
if input_type == "Image URI":
    image_uri = st.text_input("Enter the URI of the license plate image", "")
    st.write("Image URI:")
    st.write(image_uri)
    if image_uri != "":
        st.image(image=image_uri)
        if st.button("Detect license plate!"):
            get_text()
    sidebar_uri()
elif input_type == "Image File":
    image_file_buffer = st.file_uploader("Upload license plate image", type=['png', 'jpg', 'jpeg'])
    if image_file_buffer is not None:
        image = Image.open(image_file_buffer)
        st.image(image=image)
        if st.button("Detect license plate!"):
            get_text()
    sidebar_image()
else:
    picture = st.camera_input("Take a lincense plate picture!")
    if picture is not None:
        # image = Image.open(image_file_buffer)
        st.image(image=picture)
        if st.button("Detect license plate!"):
            get_text()







# image = vision.Image()
# image.source.image_uri = image_uri


# def detect_text(image, client):
#     response = client.text_detection(image=image)
#     return response
# if st.button("Get number!"):
#     response = get_text(image=image, client=client)

# for text in response.text_annotations:
#     st.write("=" * 30)
#     st.write(text.description)
#     vertices = ['(%s, %s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
#     st.write('bounds:', ",".join(vertices))