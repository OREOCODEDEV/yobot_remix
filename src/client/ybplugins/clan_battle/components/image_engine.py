from PIL import Image, ImageDraw, ImageFont, ImageChops
import os
from typing import Tuple, List
from pathlib import Path

FILE_PATH = os.path.dirname(__file__)
FONTS_PATH = os.path.join(FILE_PATH, "fonts")
FONTS = os.path.join(FONTS_PATH, "msyh.ttf")
USER_HEADERS_PATH = Path(__file__).parent.joinpath("../../../yobot_data/user_headers")


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


def user_chips(head_icon: Image.Image, user_name: str) -> Image.Image:
    head_icon = head_icon.resize((20, 20))
    head_icon = round_corner(head_icon)

    user_name_image = get_font_image(user_name, 20, (255, 255, 255))

    background = Image.new("RGBA", (15 + head_icon.width + user_name_image.width, 24), (46, 125, 50))
    background.alpha_composite(head_icon, (5, 2))
    background.alpha_composite(user_name_image, (30, center(background, user_name_image)[1]))

    return round_corner(background)


class BossStatusImageCore:
    def __init__(
        self,
        cyle: int,
        boss_round: int,
        current_hp: int,
        max_hp: int,
        name: str,
        boss_header: Image.Image,
        background_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.cyle = cyle
        self.round = boss_round
        self.background_color = background_color
        self.name = name
        self.header = boss_header

    def hp_percent_image(self) -> Image.Image:
        HP_PERCENT_IMAGE_SIZE = (340, 24)
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
        if seek_in_text_image <= 0:
            text_image = text_image_black
        elif seek_in_text_image >= text_image_white.width:
            text_image = text_image_white
        else:
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
        BOSS_HEADER_SIZE = 128

        background = Image.new("RGBA", (498, 250), self.background_color)

        boss_name_image = get_font_image(self.name, 24)
        background.alpha_composite(boss_name_image, (BOSS_HEADER_SIZE + 20, 10))
        background.alpha_composite(self.cyle_round_image(), (BOSS_HEADER_SIZE + 30 + boss_name_image.width, 10))
        background.alpha_composite(self.hp_percent_image(), (BOSS_HEADER_SIZE + 20, 44))

        background.alpha_composite(self.header, (10, 10))

        background.alpha_composite(user_chips(Image.open(USER_HEADERS_PATH.joinpath("1064988363.png")), "OREO"), (BOSS_HEADER_SIZE + 20, 78))

        return background


def generate_combind_boss_state_image(boss_state: List[BossStatusImageCore]) -> Image.Image:
    ...


# user_chips(Image.open(USER_HEADERS_PATH.joinpath("1064988363.png")), "OREO").show()
BossStatusImageCore(
    114,
    514,
    1919,
    3000,
    "野兽先辈",
    Image.new("RGBA", (128, 128), (0, 128, 128, 255)),
).generate().show()
