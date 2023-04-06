from PIL import Image, ImageDraw, ImageFont, ImageChops
import os
from typing import Tuple

FILE_PATH = os.path.dirname(__file__)
FONTS_PATH = os.path.join(FILE_PATH, "fonts")
FONTS = os.path.join(FONTS_PATH, "msyh.ttf")


def get_font_image(text: str, size: int, color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    background = Image.new("RGBA", (len(text) * size, size * 2), (255, 255, 255, 0))
    background_draw = ImageDraw.Draw(background)
    image_font = ImageFont.truetype(FONTS, size)
    background_draw.text((0, 0), text=text, font=image_font, fill=color)
    return background.crop(background.getbbox())


def center(source_image: Image.Image, target_image: Image.Image) -> Tuple[int, int]:
    result = [0, 0]
    boxes = (source_image.size, target_image.getbbox()[2:])
    for i in range(2):
        result[i] = (boxes[0][i] - boxes[1][i]) / 2
    return tuple(map(lambda i: round(i), result))


def round_corner(image: Image.Image) -> Image.Image:
    size = image.height
    circle_bg = Image.new("L", (size * 5, size * 5), 0)
    circle_draw = ImageDraw.Draw(circle_bg)
    circle_draw.ellipse((0, 0, size * 5, size * 5), 255)
    circle_bg = circle_bg.resize((size, size))

    circle_split_cursor_x = round(circle_bg.size[0] / 2)
    circle_split = (circle_bg.crop((0, 0, circle_split_cursor_x, size)), circle_bg.crop((circle_split_cursor_x, 0, size, size)))

    mask = Image.new("L", image.size, 255)
    mask.paste(circle_split[0], (0, 0))
    mask.paste(circle_split[1], (image.width - circle_split[1].width, 0))

    mask_paste_bg = Image.new("RGBA", image.size, (255, 255, 255, 0))

    return Image.composite(image, mask_paste_bg, mask)


class BossStatusImageCore:
    def __init__(
        self,
        cyle,
        boss_round,
        current_hp,
        max_hp,
        
        background_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.cyle = cyle
        self.round = boss_round
        self.background_color = background_color

    def hp_percent_image(self) -> Image.Image:
        HP_PERCENT_IMAGE_SIZE = (256, 24)
        background = Image.new("RGBA", HP_PERCENT_IMAGE_SIZE, (200, 200, 200))
        background_draw = ImageDraw.Draw(background, "RGBA")
        percent_pixel_cursor_x = round(self.current_hp / self.max_hp * HP_PERCENT_IMAGE_SIZE[0])
        background_draw.rectangle((0, 0, percent_pixel_cursor_x, HP_PERCENT_IMAGE_SIZE[1]), (255, 0, 0))

        text_str = f"{self.current_hp} / {self.max_hp}"
        text_image_white = get_font_image(text_str, 20, (255, 255, 255))
        text_image_black = get_font_image(text_str, 20)
        text_paste_center_start_cursor = center(background, text_image_white)
        text_image = Image.new("RGBA", text_image_white.size)
        seek_in_text_image = percent_pixel_cursor_x - text_paste_center_start_cursor[0] + 1
        text_image.alpha_composite(
            text_image_white.crop((0, 0, seek_in_text_image, text_image_white.size[1])),
            dest=(0, 0),
        )
        text_image.alpha_composite(
            text_image_black.crop((seek_in_text_image, 0, *text_image_black.size)),
            dest=(seek_in_text_image, 0),
        )
        background.alpha_composite(text_image, text_paste_center_start_cursor)

        return round_corner(background)

    def cyle_round_image(self) -> Image.Image:
        text_str = f"{self.cyle} 阶段， {self.round} 周目"
        text_image = get_font_image(text_str, 20, (255, 255, 255))
        background = Image.new("RGBA", (text_image.width + 24, 24), (3, 169, 244, 255))
        background.alpha_composite(text_image, center(background, text_image))
        return round_corner(background)

    def generate(self) -> Image.Image:
        ...


test = BossStatusImageCore()
test.current_hp = 47000000
test.max_hp = 100000000
test.hp_percent_image().show()
test.cyle = 4
test.round = 51
test.cyle_round_image().show()
