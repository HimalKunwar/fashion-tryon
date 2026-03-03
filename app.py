import streamlit as st
from PIL import Image
import numpy as np
from rembg import remove
import io

st.set_page_config(page_title="Virtual Try-On", layout="wide")
st.title("👕 Virtual Try-On App")

st.sidebar.header("Upload Images")
user_image = st.sidebar.file_uploader("Upload your photo (full body)", type=["jpg","jpeg","png"])
clothing_image = st.sidebar.file_uploader("Upload clothing item", type=["jpg","jpeg","png"])

def remove_background(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    result = remove(buf.getvalue())
    return Image.open(io.BytesIO(result)).convert("RGBA")

def overlay_clothing(person_img, clothing_img):
    person = person_img.convert("RGBA")
    clothing = remove_background(clothing_img)

    pw, ph = person.size
    cw, ch = clothing.size

    # scale clothing to 60% of person width
    target_w = int(pw * 0.6)
    scale = target_w / cw
    target_h = int(ch * scale)
    clothing = clothing.resize((target_w, target_h), Image.LANCZOS)

    # paste at center-top area (torso)
    paste_x = (pw - target_w) // 2
    paste_y = int(ph * 0.2)

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