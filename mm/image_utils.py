from io import BytesIO
from cairosvg import svg2png
from PIL import Image


class ImageUtils:

    @staticmethod
    def svg_to_jpg(svg_file, jpg_file, width=None, height=None):
        png_data = svg2png(url=svg_file, output_width=width,
                           output_height=height)

        # Convert PNG to JPG
        image = Image.open(BytesIO(png_data))
        # Convert to RGB mode if the image has transparency
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image,
                             mask=image.split()[3])  # 3 is the alpha channel
            image = background
        image.save(jpg_file, 'JPEG', quality=95)

        return jpg_file
