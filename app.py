from urllib import response
import streamlit as st
from google.cloud import vision
import io

input_type = st.radio("Select input", ("Image URI", "Image File"), horizontal=True)
if input_type == "Image URI":
    image_uri = st.text_input("Enter the URI of the license plate image", "")
    st.write(f"Image URI: {image_uri}")
else:
    st.file_uploader("Upload license plate image")
    st.write("Not available yet.")

client = vision.ImageAnnotatorClient()
image = vision.Image()
image.source.image_uri = image_uri


def get_text(image):
    response = client.text_detection(image=image)
    return response
response = get_text(image=image)

for text in response.text_annotations:
    st.write("=" * 30)
    st.write(text.description)
    vertices = ['(%s, %s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
    st.write('bounds:', ",".join(vertices))