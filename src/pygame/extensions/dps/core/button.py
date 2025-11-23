import dataclasses
from typing import Callable

import pygame

from . import io, types


@dataclasses.dataclass
class TextOptions(io.Configurable):
    font: pygame.font.Font
    antialias: bool
    color: types.ColorValue
    hover_color: types.ColorValue


@dataclasses.dataclass
class SpriteOptions(io.Configurable):
    topleft: types.Coordinate = (0, 0)
    image: pygame.Surface | None = None
    layer: int = 0


@dataclasses.dataclass
class ButtonOptions(SpriteOptions):
    text: str = ""
    color: types.ColorValue = ""
    text_opts: TextOptions | None = None
    width: float = 0
    height: float = 0


class Button(pygame.sprite.DirtySprite):
    """Clickable image or text button

    Args:
        opts (ButtonOptions): configuration options for the button
        on_click (Callable): on-click callback
    """

    _hovered: bool = False

    def __init__(self, opts: ButtonOptions, on_click: Callable):
        super().__init__()

        image_size = (opts.width, opts.height)
        self.image = opts.image if opts.image else pygame.Surface(image_size)

        self.opts = opts
        self.on_click = on_click

        self.rect = self.image.get_rect()
        self.rect.update(opts.topleft, image_size)

    def update(self):
        if self.opts.text and self.opts.text_opts is not None:
            text_opts = self.opts.text_opts

            text_color = text_opts.hover_color if self.hovered else text_opts.color
            img = text_opts.font.render(self.opts.text, text_opts.antialias, text_color)
            w, h = img.get_size()
            pos = (self.rect.centerx - (w / 2), self.rect.centery - (h / 2))

            self.image.fill(self.opts.color)
            self.image.blit(img, pos)

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, hovered):
        # only dirty the sprite if we're changing state
        if self._hovered is not hovered:
            self.dirty = 1
        self._hovered = hovered
