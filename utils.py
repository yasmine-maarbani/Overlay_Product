import os
import logging
import dotenv
import boto3
from PIL import Image
from botocore.exceptions import ClientError
import requests

dotenv.load_dotenv()


def upload_to_aws(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
    )
    try:
        _ = s3_client.upload_file(file_name, bucket, object_name)
        s3_url = f"https://{os.environ['BUCKET_NAME']}.s3.amazonaws.com/{object_name}"
    except ClientError as error:
        logging.error(error)
        return False, None
    return True, s3_url


def patch(img: Image.Image, bg: Image.Image) -> Image.Image:
    """patch the image onto the background

     :param img: the image
     :param bg: the background
     :return: the patched image and the offset
     """
    img_w, img_h = img.size
    bg_w, bg_h = bg.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    bg.paste(img, offset, img)
    return bg


def calculate_width_height(product_img_size, aspect_ratio=None, res_img_size=None):
    if aspect_ratio is None:
        width, height, product_img_ratio, res_img_ratio = res_img_size[0], res_img_size[1], \
            product_img_size[0] / product_img_size[1], res_img_size[0] / res_img_size[1]
    else:
        product_img_ratio, res_img_ratio = aspect_ratio[0] / aspect_ratio[1], aspect_ratio[0] / aspect_ratio[1]
        if res_img_ratio > 1:
            width = 768
            height = int(width / res_img_ratio)
        elif res_img_ratio < 1:
            height = 768
            width = int(height * res_img_ratio)
        else:
            width = height = 768

    if res_img_ratio > 1:
        product_img_height = int(height * 0.8)
        product_img_width = int(product_img_size * product_img_ratio)
    elif res_img_ratio < 1:
        product_img_width = int(width * 0.6)
        product_img_height = int(product_img_width / product_img_ratio)
    else:
        product_img_width = int(width * 0.55)
        product_img_height = int(product_img_width / product_img_ratio)

    return width, height, product_img_width, product_img_height


def generate_images(prompt, aspect_ratio=None, num_images=1, size=None):
    """Generate the images

    :param prompt: the prompt
    :param aspect_ratio: the aspect ratio
    :param num_images: the number of images to generate
    :param size: the size of the image
    :return: the generated images
    """

    product_img_path = [f for f in os.listdir("./") if f.endswith("_cleaned.png")][0].replace(" ", "_")
    clean_product_image = Image.open(product_img_path)

    width, height, product_img_width, product_img_height = calculate_width_height(
        clean_product_image.size, aspect_ratio, size)

    clean_product_image = clean_product_image.resize((product_img_width, product_img_height))

    background = Image.open("gray_background.jpeg")

    # resize the background image to match aspect ratio
    background = background.resize((width, height))

    # paste the product image onto the bg
    background = patch(clean_product_image.convert("RGBA"), background)

    background.save('base_image_' + product_img_path)

    res1, url1 = upload_to_aws('base_image_' + product_img_path, os.environ["BUCKET_NAME"])

    black_product_image = clean_product_image.convert('RGBA')

    # Get the pixel data
    pixels = black_product_image.load()

    # Loop through each pixel and color the product in black
    for i in range(black_product_image.size[0]):
        for j in range(black_product_image.size[1]):
            if pixels[i, j][3] != 0:
                pixels[i, j] = (0, 0, 0, 255)
            else:
                pixels[i, j] = (255, 255, 255, 255)

    white_background = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    white_background = patch(black_product_image, white_background)

    white_background.save('product_mask_' + product_img_path)

    res2, url2 = upload_to_aws('product_mask_' + product_img_path, os.environ["BUCKET_NAME"])

    if res1 and res2:
        json = {
            "key": os.environ["SD_API_KEY"],
            "model_id": os.environ["MODEL_ID"],
            "controlnet_model": "canny",
            "prompt": prompt,
            "negative_prompt": "",
            "init_image": url1,
            "mask_image": url2,
            "width": width,
            "height": height,
            "samples": num_images,
            "num_inference_steps": 31,
            "safety_checker": "no",
            "enhance_prompt": "no",
            "scheduler": "EulerAncestralDiscreteScheduler",
            "guidance_scale": 7,
            "strength": 1,
            "seed": None,
            "webhook": None,
            "auto_hint": "yes",
            "track_id": None
        }
        res_json = requests.post(os.environ["SD_API_URL"], json=json).json()

        while res_json["status"] == "failed":
            res_json = requests.post(os.environ["SD_API_URL"], json=json).json()

        res = res_json["output"]
        res_id = res_json["id"]

        while not res:
            response = requests.post(
                "https://stablediffusionapi.com/api/v4/dreambooth/fetch",
                json={"key": os.environ["SD_API_KEY"], "request_id": res_id},
                timeout=200,
            )
            if response.json()["status"] == "success":
                res = response.json()["output"]
                break
            elif response.json()["status"] == "failed":
                res_json = requests.post(os.environ["SD_API_URL"], json=json).json()
                res = res_json["output"]
                res_id = res_json["id"]

        final_images = []
        for img_url in res:
            img = Image.open(requests.get(img_url, stream=True).raw).convert("RGBA")
            img = patch(clean_product_image, img)
            path = "output_dir/" + img_url.split("/")[-1]
            img.save(path)
            final_images.append(path)

        return final_images

    else:
        return None
