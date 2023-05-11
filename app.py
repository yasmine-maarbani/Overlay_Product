import os
import streamlit as st
import numpy as np
from streamlit_cropper import st_cropper
from rembg import remove
from PIL import Image
from components import form_input
import constants
import utils

st.set_option('deprecation.showfileUploaderEncoding', False)

st.set_page_config(page_title="AI Product Placement", page_icon=Image.open('logo.png'))

st.markdown("""
<style>
footer {visibility : hidden;}
</style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 1

if 'product' not in st.session_state:
    st.session_state.product = None


def clear_images(skip=None):
    for file in os.listdir("./"):
        if file not in ["logo.png", "gray_background.jpeg"]:
            if file.split('.')[-1] in ["png", "jpg", "jpeg"] and file != skip:
                os.remove(file)


if st.session_state.page == 1:
    st.title('Create AI Product Images :sparkles:')
    tab1, tab2 = st.tabs(["Step 1", "Step 2"])

    with tab1:
        st.header("Upload Your Product :frame_with_picture:")
        uploaded_product = st.file_uploader("Upload Your Product", type=["png", "jpg", "jpeg"],
                                            label_visibility='collapsed')
        if uploaded_product:
            st.session_state.product = None

        # reuse the uploaded product in case of regenerate
        if st.session_state.product is not None:
            product_path = st.session_state.product
            clear_images(skip=st.session_state.product)
            st.header(":warning: :red[Reusing the uploaded product]")
            st.subheader("you can upload a new one if you want")
        else:

            # crop the product
            realtime_update = st.checkbox(label="Update in Real Time", value=True)

            if uploaded_product:
                img = Image.open(uploaded_product)
                if not realtime_update:
                    st.write("Double click to save crop")

                st.write("Make sure your product fits in the box")

                cropped_img = st_cropper(img, realtime_update=realtime_update)
                cropped_img = Image.fromarray(np.uint8(cropped_img))

                clear_images()

                # extract the product
                cleaned = remove(cropped_img)

                product_path = st.session_state.product or f"product_" \
                                                           f"{uploaded_product.name.split('.')[0].replace(' ','_')}" \
                                                           f"_cleaned.png"
                cleaned.save(product_path)

                st.header("Preview")

                st.write("Cropped")
                st.image(cropped_img)

                st.write("Cleaned")
                st.image(cleaned)

    with tab2:
        prompt = 'a product shot of a '

        pt = st.header(prompt)
        generate = st.button("Generate", type="primary", use_container_width=True)
        aspect_choice = st.selectbox(label="Aspect Ratio", options=("1:1", "16:9", "4:3", "9:16", "3:4"))
        aspect_dict = {
            "1:1": (1, 1),
            "16:9": (16, 9),
            "4:3": (4, 3),
            "9:16": (9, 16),
            "3:4": (3, 4),
        }
        aspect_ratio = aspect_dict[aspect_choice]

        num_images = st.slider("number of images to generate", 1, 3, step=1)

        # selecting a product
        product = st.text_input('Product', placeholder='bottle', max_chars=30)
        if product:
            prompt = prompt + product
        else:
            prompt = prompt + 'product'

        # selecting a placement
        prompt = form_input(1,
                            "Placement",
                            constants.placement_select_options,
                            "Placement-text",
                            "Example : on a smooth circular gradient platform",
                            constants.placement_options,
                            prompt)

        # selecting a surrounding
        prompt = form_input(2,
                            "Surrounding",
                            constants.surrounding_select_options,
                            "Surrounding-text",
                            "Example : next to flowers",
                            constants.surrounding_options,
                            prompt)

        # selecting a background
        prompt = form_input(3,
                            "Background",
                            constants.background_select_options,
                            "Background-text",
                            "Example : in front of a gradient background",
                            constants.background_options,
                            prompt)

        pt.text_area('prompt', value=prompt, disabled=True)

        if generate:
            if uploaded_product or st.session_state.product:
                st.session_state.product = product_path
                st.session_state.prompt = prompt
                st.session_state.aspect_ratio = aspect_ratio
                st.session_state.num_images = num_images
                st.session_state.page = 2
                st.experimental_rerun()
            else:
                pt.error("Please enter a product")

elif st.session_state.page == 2:
    st.title("Generating Images :hourglass_flowing_sand:")
    st.subheader("This might take a while")
    res = utils.generate_images(st.session_state.prompt, st.session_state.aspect_ratio, st.session_state.num_images)

    if res:
        st.session_state.results = res
        st.session_state.page = 3
        st.experimental_rerun()
    else:
        st.error("Something went wrong :(")

elif st.session_state.page == 3:
    st.title('Your product Placement images are ready :sparkles:')
    num_images = len(st.session_state.results)

    cols = st.columns(num_images)

    if "output_dir" not in os.listdir("./"):
        os.mkdir("output_dir")

    for i, col in enumerate(cols):
        col.image(st.session_state.results[i], use_column_width=True)

        with open(st.session_state.results[i], "rb") as image:
            col.download_button(label="Download", data=image, file_name=f"result_{i}.png")

    if st.button("Get creative again", type="primary", use_container_width=True):
        st.session_state.page = 1
        st.experimental_rerun()
