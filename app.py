import streamlit as st
import numpy as np
from streamlit_cropper import st_cropper
from rembg import remove
from PIL import Image
import constants

st.set_option('deprecation.showfileUploaderEncoding', False)

st.set_page_config(page_title="AI Product Placement", page_icon=Image.open('logo.png'))

st.markdown("""
<style>
section[data-testid="stSidebar"] {display: none;}
footer {visibility : hidden;}
</style>
""", unsafe_allow_html=True)

st.title('Create AI Product Images :sparkles:')
tab1, tab2 = st.tabs(["Step 1", "Step 2"])

with tab1:
    st.header("Upload Your Product :frame_with_picture:")
    uploaded_product = st.file_uploader("Upload Your Product", type=["png", "jpg", "jpeg"],
                                        label_visibility='collapsed')

    # crop the product
    realtime_update = st.checkbox(label="Update in Real Time", value=True)

    if uploaded_product:
        img = Image.open(uploaded_product)
        if not realtime_update:
            st.write("Double click to save crop")

        st.write("Make sure your product fits in the box")

        cropped_img = st_cropper(img, realtime_update=realtime_update)
        cropped_img = Image.fromarray(np.uint8(cropped_img))
        cropped_img.save("cropped.png")

        # extract the product
        cleaned = remove(cropped_img)

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
        prompt = prompt + '[product]'

    # selecting a placement
    placement_select = st.selectbox('Placement', constants.placement_select_options)
    if placement_select == "custom":
        placement_text = st.text_input('Placement-text', label_visibility='collapsed',
                                       placeholder='Example : on a smooth circular gradient platform',
                                       max_chars=30)
        prompt = prompt + ' ' + placement_text
    elif placement_select == "None":
        pass
    else:
        placement_text = st.selectbox('Placement-text',
                                      constants.placement_options,
                                      label_visibility='collapsed')
        prompt = prompt + ' ' + placement_select + ' ' + placement_text

    # selecting a surrounding
    surrounding_select = st.selectbox('Surrounding', constants.surrounding_select_options)
    if surrounding_select == "custom":
        surrounding_text = st.text_input('Surrounding-text', label_visibility='collapsed',
                                         placeholder='Example : next to flowers', max_chars=30)
        prompt = prompt + ", " + surrounding_text
    elif surrounding_select == "None":
        pass
    else:
        surrounding_text = st.selectbox('Surrounding-text',
                                        constants.surrounding_options,
                                        label_visibility='collapsed')
        prompt = prompt + ", " + surrounding_select + ' ' + surrounding_text

    # selecting a background
    background_select = st.selectbox('Background', constants.background_select_options)
    if background_select == "custom":
        background_text = st.text_input('Background-text', label_visibility='collapsed',
                                        placeholder='Example : in front of a gradient background', max_chars=30)
        prompt = prompt + ", " + background_text
    elif background_select == "None":
        pass
    else:
        background_text = st.selectbox('Background-text',
                                       constants.background_options,
                                       label_visibility='collapsed')
        prompt = prompt + ", " + background_select + ' ' + background_text

    pt.text_area('prompt', value=prompt, disabled=True)
