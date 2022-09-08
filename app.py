import streamlit as st

image_uri = st.text_input("Input license plate image uri", "")
st.write(image_uri)