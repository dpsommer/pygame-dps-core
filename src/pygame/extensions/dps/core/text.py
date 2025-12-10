import dataclasses
from typing import List

import pygame

from . import io, types


@dataclasses.dataclass
class TextOptions(io.Configurable):
    font: pygame.font.Font
    antialias: bool
    color: types.ColorValue
    hover_color: types.ColorValue


def draw_text(
    text: str, opts: TextOptions, surf: pygame.Surface, pos: types.Coordinate
) -> pygame.Surface:
    img = opts.font.render(text, opts.antialias, opts.color)
    surf.blit(img, pos)
    return img


def draw_multiline_text(
    text: str, opts: TextOptions, surf: pygame.Surface, pos: types.Coordinate
) -> pygame.Surface | List[pygame.Surface]:
    x, top = pos
    line_height = opts.font.get_linesize()
    text_boxes = []

    for i, line in enumerate(text.splitlines()):
        y = (i * line_height) + top
        text_boxes.append(draw_text(line, opts, surf, (x, y)))

    return text_boxes
