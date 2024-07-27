from PIL import Image


def image_compress(image_path, width, height):
    with Image.open(image_path) as img:
        img = img.resize((width, height))
        img.save(image_path, quality=95)
