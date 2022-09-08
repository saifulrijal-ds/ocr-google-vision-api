import streamlit as st
from google.cloud import vision
import io

image_uri = st.text_input("Enter the URI of the license plate image", "")
st.write(f"Image URI: {image_uri}")