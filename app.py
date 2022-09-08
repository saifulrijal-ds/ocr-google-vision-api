import streamlit as st
from __future__ import print_function
from google.cloud import vision
import io

image_uri = st.text_input("Input license plate image uri", "")
st.write(image_uri)