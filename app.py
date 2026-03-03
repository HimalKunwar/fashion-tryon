import streamlit as st
from PIL import Image
import numpy as np
import mediapipe as mp
from rembg import remove
import io
import cv2

st.set_page_config(page_title="Virtual Try-On", layout="wide")
st.title("👕 Virtual Try-On App")

st.sidebar.header("Upload Images")
user_image = st.sidebar.file_uploader("Upload your photo (full body)", type=["jpg","jpeg","png"])
clothing_image = st.sidebar.file_uploader("Upload clothing item", type=["jpg","jpeg","png"])

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def get_body_landmarks(img):
    img_rgb = np.array(img.convert("RGB"))
    with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
        results = pose.process(img_rgb)
    return results.pose_landmarks, img_rgb.shape

def remove_background(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    result = remove(buf.getvalue())
    return Image.open(io.BytesIO(result)).convert("RGBA")

def overlay_clothing(person_img, clothing_img):
    landmarks, shape = get_body_landmarks(person_img)
    ph, pw = shape[:2]

    clothing = remove_background(clothing_img)

    if landmarks:
        lm = landmarks.landmark
        # get shoulder positions
        left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]

        # calculate torso dimensions
        shoulder_width = abs(left_shoulder.x - right_shoulder.x) * pw
        torso_height = abs(left_shoulder.y - left_hip.y) * ph

        target_w = int(shoulder_width * 1.8)
        target_h = int(torso_height * 1.6)

        clothing = clothing.resize((target_w, target_h), Image.LANCZOS)

        # center between shoulders
        center_x = int((left_shoulder.x + right_shoulder.x) / 2 * pw)
        top_y = int(min(left_shoulder.y, right_shoulder.y) * ph)

        paste_x = center_x - target_w // 2
        paste_y = top_y - int(ph * 0.02)

    else:
        # fallback if no pose detected
        target_w = int(pw * 0.6)
        scale = target_w / clothing.width
        target_h = int(clothing.height * scale)
        clothing = clothing.resize((target_w, target_h), Image.LANCZOS)
        paste_x = (pw - target_w) // 2
        paste_y = int(ph * 0.2)

    person = person_img.convert("RGBA")
    result = person.copy()
    result.paste(clothing, (paste_x, paste_y), clothing)
    return result

if user_image and clothing_image:
    person = Image.open(user_image)
    clothing = Image.open(clothing_image)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Your Photo")
        st.image(person)
    with col2:
        st.subheader("Clothing Item")
        st.image(clothing)

    if st.button("Try On 👕"):
        with st.spinner("Processing..."):
            result = overlay_clothing(person, clothing)
            with col3:
                st.subheader("Result")
                st.image(result)
else:
    st.info("Upload both your photo and a clothing item to get started.")