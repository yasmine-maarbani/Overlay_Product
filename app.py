import streamlit as st
import os
from PIL import Image
from rembg import remove


class OverlayProductApp:

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
                    os.mkdir(bg_path)
                else:
                    for img in os.listdir(bg_path):
                        os.remove(os.path.join(bg_path, img))
                for i in range(len(uploaded_bg)):
                    bg_file_path = os.path.join(bg_path, uploaded_bg[i].name)
                    with open(bg_file_path, "wb") as f:
                        f.write(uploaded_bg[i].getbuffer())

                output_dir = 'output_dir'
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                else:
                    for img in os.listdir(output_dir):
                        os.remove(os.path.join(output_dir, img))

            except OSError as e:
                st.write("Error occurred while saving background image: ", e)
                return
            st.write("Result:")
            self.overlay_product(uploaded_product.name, bg_path)

            for output_image_path in os.listdir(output_dir):
                st.image(os.path.join(output_dir, output_image_path))

    @staticmethod
    def overlay_product(product_path, background_path):
        output_dir = 'output_dir'

        input_img = Image.open(product_path)
        cleaned = remove(input_img)

        for i, bg in enumerate(os.listdir(background_path)):
            background = Image.open(os.path.join(background_path, bg))
            bg_w, bg_h = background.size

            resized = cleaned.resize((int(min(bg_w, bg_h) * 0.75), int(min(bg_w, bg_h) * 0.75)))
            img_w, img_h = resized.size

            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)

            background.paste(resized, offset, resized)

            output_path = os.path.join(output_dir, f"{i}.jpg")
            background.save(output_path)


# Call the app
app = OverlayProductApp()
app.construct_app()
