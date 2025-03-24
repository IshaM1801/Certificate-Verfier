import streamlit as st
import cv2
import pytesseract
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
from PIL import Image

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def process_image(uploaded_file):
    # Convert the uploaded file to an OpenCV image
    image = Image.open(uploaded_file)
    image = np.array(image)

    if image is None:
        st.error("Error: Image file not found or unable to open.")
        return

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding for better OCR accuracy
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Extract text using Tesseract OCR
    text = pytesseract.image_to_string(gray)

    # Regex pattern to extract Coursera verification URLs (handles missing "https")
    url_pattern = r"(?:https?://)?coursera\.org/verify/[A-Za-z0-9]+"
    urls = re.findall(url_pattern, text)

    if urls:
        # Ensure the extracted URL has "https://" prefix
        certificate_url = urls[0] if urls[0].startswith("http") else "https://" + urls[0]
        st.write(f"Extracted URL: {certificate_url}")

        try:
            # Send request to Coursera for verification
            response = requests.get(certificate_url)

            if response.status_code == 200:
                # Parse response text to check for validity
                if "Coursera certifies their successful completion" in response.text:
                    st.success("✅ Certificate is valid.")
                else:
                    st.warning("⚠️ Certificate may not be valid.")
            else:
                st.error(f"❌ Error accessing the verification page. Status code: {response.status_code}")
        except requests.RequestException as e:
            st.error(f"❌ Request failed: {e}")
    else:
        st.warning("⚠️ No URL found in the certificate.")

# Streamlit app layout
st.title("🎓 Coursera Certificate Verification App")
st.write("📜 Upload an image of the certificate to verify its validity.")

# File uploader
uploaded_file = st.file_uploader("📂 Choose an image file", type=["jpg", "jpeg", "png"])

# Process the uploaded file
if uploaded_file:
    process_image(uploaded_file)
