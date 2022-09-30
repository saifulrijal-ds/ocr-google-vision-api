# Import libraries and packages.
import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import numpy as np
import cv2
import re

# Set streamlit page configuration.
st.set_page_config(
    page_title="License Plate Detection",
    page_icon=":oncoming_police_car:",
    initial_sidebar_state="collapsed" )

# Define some function
def sidebar_uri():
    """Add example URI in sidebar"""
    st.sidebar.write("You can use this URI's example:")
    st.sidebar.code("gs://ocr-361804/license_plate_images/plat1.jpg", language="http")
    st.sidebar.code("https://storage.googleapis.com/ocr-361804/license_plate_images/plat2.jpg", language="http")

def sidebar_image():
    """Add sample image in sidebar."""
    st.sidebar.write("You can download this sample image:")
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
    """Detect text in the image."""
    # Instantiate API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = vision.ImageAnnotatorClient(credentials=credentials)

    def get_image_uri(image_uri):
        """Get image from URI."""
        image = vision.Image()
        image.source.image_uri = image_uri
        return image

    def get_image_upload(image_file_buffer):
        """Get image from uploaded image file buffer."""
        content = image_file_buffer.getvalue()
        return vision.Image(content=content)
    
    def get_image_picture(picture):
        """Get image from captured image file buffer."""
        content = picture.getvalue()
        return vision.Image(content=content)

    # Select method of get image based user option.
    if input_type == "Image URI":
        image = get_image_uri(image_uri=image_uri)
    elif input_type == "Image File":
        image = get_image_upload(image_file_buffer=image_file_buffer)
    else:
        image = get_image_picture(picture=picture)

    # Perform text detection on the image file.
    response = client.text_detection(
        image=image, 
        image_context={"language_hints": ["id"]}
        )

    # Get response and process the response.
    if response.error.message:
        with st.expander("See error message"):
            st.exception(Exception('{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message)))
    else:     
        with st.expander("See all detected text"):
            for text in response.text_annotations:
                st.text("=" * 30)
                st.text(text.description)
                vertices = ['(%s, %s)' % (v.x, v.y) for v in text.bounding_poly.vertices]
                st.write('bounds:', ",".join(vertices))

        main_text = response.text_annotations[0].description

        def clean_the_text(text):
            """Remove non alphanumeric chars."""
            # substitute non alphanumeric to a space
            non_alphanum_pattern = re.compile(r"[^a-zA-Z0-9\s]+")
            cleaned_text = non_alphanum_pattern.sub(" ", text)
            # clean double or more whitespace
            more_whitespace_pattern = re.compile(r"\s{2,}")
            cleaned_text = more_whitespace_pattern.sub(" ", cleaned_text)
            return cleaned_text

        cleaned_text = clean_the_text(main_text)


        # Get the possible texts.
        plate_number_regex = re.compile(r"^([A-Z]{1,2})\s?(\d{1,4})\s?([A-Z]{1,3})$", flags=re.MULTILINE)
        num_plate = plate_number_regex.search(cleaned_text)

        nik_regex = re.compile(r"\d{16}")
        nik = nik_regex.search(cleaned_text)

        chasis_number_regex = re.compile(r"[\w\d]{10,12}([\d]{5})")
        chasis_number = chasis_number_regex.search(cleaned_text)


        # Create html class for text formatting.
        st.markdown("""
        <style>
        .big-font {
            font-size:100px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        .medium-font {
            font-size:50px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Show result in streamlit page.
        if num_plate is not None:
            st.markdown(f'<p class="big-font">{num_plate.group(0)}</p>', unsafe_allow_html=True)
            st.markdown(f"Region Code: **{num_plate.group(1)}**\n\nRegistration Number: **{num_plate.group(2)}** \n\nLetter Series: **{num_plate.group(3)}**")
            if chasis_number is not None:
                st.markdown(f'<p class="medium-font">{chasis_number.group(0)}</p>', unsafe_allow_html=True)
                st.markdown(f"Last 5 digits of chasis number: **{chasis_number.group(1)}**")
        elif nik is not None:
            st.markdown(f'<p class="medium-font">{nik.group(0)}</p>', unsafe_allow_html=True)
        elif chasis_number is not None:
            st.markdown(f'<p class="medium-font">{chasis_number.group(0)}</p>', unsafe_allow_html=True)
            st.markdown(f"Last 5 digits of chasis number: **{chasis_number.group(1)}**")
        else:
            st.markdown('<p class="medium-font">License plate, ID, or Chasis number not found!</p>', unsafe_allow_html=True)

        def draw_ocr_results(image, text, rect, color=(0, 255, 0)):
            """Draw boundary and text of ocr result in image."""
            (startX, startY, endX, endY) = rect
            cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
            cv2.putText(image, text, (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            return image

        cv2_image = Image.open(image_file_buffer)
        cv2_image = np.array(cv2_image)
        cv2_final_image = cv2_image.copy()

        for text in response.text_annotations[1::]:
            ocr = text.description
            startX = text.bounding_poly.vertices[0].x
            startY = text.bounding_poly.vertices[0].y
            endX = text.bounding_poly.vertices[1].x
            endY = text.bounding_poly.vertices[2].y

            rect = (startX, startY, endX, endY)

            final = draw_ocr_results(cv2_final_image, ocr, rect)

        st.image(final)

        
st.title("License Plate, ID, and Chasis Number Detection")

input_type = st.radio("Select input", ("Image URI", "Image File", "Take a Picture"), horizontal=True)
if input_type == "Image URI":
    image_uri = st.text_input("Enter the URI of the license plate, id card, or vehilce registration image", "")
    st.warning(
        """Caution: When fetching images from HTTP/HTTPS URLs, Google cannot guarantee that the request will be completed. 
        Your request may fail if the specified host denies the request (for example, due to request throttling or DOS prevention), or if Google throttles requests to the site for abuse prevention. [More information](https://cloud.google.com/vision/docs/ocr#detect_text_in_a_remote_image).""", icon="⚠️")
    if image_uri != "":
        st.write("Image URI:")
        st.write(image_uri)
        st.image(image=image_uri)
        if st.button("Detect license plate, id, or chasis number!"):
            get_text()
    sidebar_uri()
elif input_type == "Image File":
    image_file_buffer = st.file_uploader("Upload license plate, id card, or vehicle registration image", type=['png', 'jpg', 'jpeg'])
    if image_file_buffer is not None:
        image = Image.open(image_file_buffer)
        st.image(image=image)
        if st.button("Detect license plate, id, or chasis number!"):
            get_text()
    sidebar_image()
else:
    picture = st.camera_input("Take a lincense plate, id card, or vehicle registration picture!")
    if picture is not None:
        st.image(image=picture)
        if st.button("Detect license plate, id, or chasis number!"):
            get_text()