import cv2
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time
import json
import streamlit as st
import numpy as np

# Google Sheets setup
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("qr.json")
client = gspread.authorize(creds.with_scopes(scope))

# Open your Google Sheet
sheet_id = "1GSOkG9dGjH76OdMTDJsym8QvVTDuOaXJhhhWHf-yI6c"
spreadsheet = client.open_by_key(sheet_id)
worksheet = spreadsheet.sheet1  # Opens the first sheet/tab in the spreadsheet

# Streamlit app setup
st.title("QR Code Scanner")
st.text("Make sure your webcam is working")

# Initialize webcam
cap = cv2.VideoCapture(0)

# Set a delay time between scans (in seconds)
scan_delay = 2
last_scanned_data = None

while True:
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to capture image from webcam.")
        break

    # Convert the frame to RGB format for display in Streamlit
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qr_code_detector = cv2.QRCodeDetector()
    decoded_text, points, _ = qr_code_detector.detectAndDecode(frame)

    if decoded_text:
        # Check if the data is different from the last scanned data
        if decoded_text != last_scanned_data:
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')

            try:
                # Parse the JSON data
                qr_data_dict = json.loads(decoded_text)

                # Extract the values from the dictionary
                name = qr_data_dict.get("name", "")
                roll = qr_data_dict.get("roll", "")
                position = qr_data_dict.get("position", "")

                # Append data to Google Sheet
                worksheet.append_row([date, time_str, name, roll, position])

                # Update last scanned data
                last_scanned_data = decoded_text

                st.success(f"Scanned QR Code: {decoded_text} on {date} at {time_str}")

                # Introduce a delay after a successful scan
                time.sleep(scan_delay)

            except json.JSONDecodeError:
                st.error("Failed to decode QR data as JSON. Skipping.")

    # Display the frame in Streamlit
    st.image(frame_rgb)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
