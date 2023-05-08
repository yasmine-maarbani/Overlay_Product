import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import constants

st.set_option('deprecation.showfileUploaderEncoding', False)

st.set_page_config(page_title="AI Product Placement", page_icon=Image.open('logo.png'))

st.markdown("""
<style>
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
    aspect_choice = st.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3"])
    flip = st.checkbox(label="Flip the aspect ratio", value=False)
    aspect_dict = {
        "1:1": (1, 1),
        "16:9": (16, 9),
        "4:3": (4, 3),
    }
    aspect_ratio = aspect_dict[aspect_choice]
    if flip:
        aspect_ratio = aspect_ratio[::-1]

    if uploaded_product:
        img = Image.open(uploaded_product)
        if not realtime_update:
            st.write("Double click to save crop")
        # Get a cropped image from the frontend
        st.write("Make sure your product fits in the box")
        cropped_img = st_cropper(img, realtime_update=realtime_update,
                                 aspect_ratio=aspect_ratio)
        # Manipulate cropped image at will
        st.write("Preview")
        st.image(cropped_img)

with tab2:
    prompt = 'a product shot of a '

    pt = st.header(prompt)
    st.button("Generate", type="primary", use_container_width=True)

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

    num_images = st.slider("number of images to generate", 1, 3, step=1)
    pt.text_area('prompt', value=prompt, disabled=True)
