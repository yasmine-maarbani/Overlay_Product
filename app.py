import shutil

import streamlit as st
import os
from PIL import Image
from rembg import remove


class Overlay_Product_App:
    
    def construct_app(self):
        st.title("Overlay Product")
        uploaded_product = st.file_uploader("Upload Your Product")
        uploaded_bg = st.file_uploader("Upload Your Background", accept_multiple_files=True)
        bg_path = "backgrounds"
        if uploaded_product:
            with open(uploaded_product.name, "wb") as f:
                f.write(uploaded_product.getbuffer())
        if uploaded_bg:
            try:
                if not os.path.exists(bg_path):
                    os.makedirs(bg_path)
                else:
                    for img in os.listdir(bg_path):
                        os.remove(os.path.join(bg_path, img))
                for i in range(len(uploaded_bg)):
                    bg_file_path = os.path.join(bg_path, uploaded_bg[i].name)
                    with open(bg_file_path, "wb") as f:
                        f.write(uploaded_bg[i].getbuffer())

                Output_dir = 'Output_dir'
                for img in os.listdir(Output_dir):
                    os.remove(os.path.join(Output_dir, img))

            except OSError as e:
                st.write("Error occurred while saving background image: ", e)
                return
            st.write("Result:")
            self.overlay_product(uploaded_product.name, bg_path)

            for output_image_path in os.listdir(Output_dir):
                st.image(os.path.join(Output_dir, output_image_path))

    def overlay_product(self, Product_Path, Background_Path):
        Output_dir = 'Output_dir'

        input_img = Image.open(Product_Path)
        cleaned = remove(input_img)

        for i, bg in enumerate(os.listdir(Background_Path)):
            # print(os.path.join(Background_Path, bg))
            background = Image.open(os.path.join(Background_Path, bg))
            bg_w, bg_h = background.size
            resized = cleaned.resize((int(min(bg_w, bg_h) * 0.75), int(min(bg_w, bg_h) * 0.75)))
            img_w, img_h = resized.size
            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
            background.paste(resized, offset, resized)
            output_path = os.path.join(Output_dir, f"{i}.jpg")
            background.save(output_path)


# Call the app
app = Overlay_Product_App()
app.construct_app()
