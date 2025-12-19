import dataclasses
from typing import List

import pygame

from pygame_dps_core import const, io, key, types


@dataclasses.dataclass(frozen=True)
class SpriteOptions(io.Configurable):
    topleft: types.Coordinate = (0, 0)
    width: int = 0
    height: int = 0
    image: pygame.Surface | None = None
    layer: int = 0


@dataclasses.dataclass(frozen=True)
class AnimationOptions(io.Configurable):
    name: str
    repeat: int


@dataclasses.dataclass(frozen=True)
class SpriteSheetSettings(io.Configurable):
    sprite_sheet: pygame.Surface
    sprite_width: int
    sprite_height: int
    animation_opts: List[AnimationOptions]


@dataclasses.dataclass(frozen=True)
class Margins(io.Configurable):
    top: int = 0
    left: int = 0
    right: int = 0
    bottom: int = 0

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Returns a copy of the given Rect with margins applied

        Rect position is moved by (left, top) and size is shrunk by
        ((left + right), (top + bottom)).

        Args:
            rect (pygame.Rect): Rect to apply margins to

        Returns:
            pygame.Rect: the resulting Rect with updated position and size
        """
        topleft = (rect.left + self.left, rect.top + self.top)
        margin_rect = rect.inflate(-(self.left + self.right), -(self.top + self.bottom))
        margin_rect.topleft = topleft
        return margin_rect


@dataclasses.dataclass(frozen=True)
class TextOptions(io.Configurable):
    font: pygame.font.Font
    color: types.ColorValue
    bg_color: types.ColorValue | None = None
    antialias: bool = True
    justify: bool = False
    align: types.HorizontalAlignment = dataclasses.field(
        default=types.HorizontalAlignment.LEFT
    )
    vertical_align: types.VerticalAlignment = dataclasses.field(
        default=types.VerticalAlignment.TOP
    )


@dataclasses.dataclass(frozen=True)
class TypewriterTextOptions(TextOptions):
    text_speed: int = const.DEFAULT_TEXT_SPEED
    framerate: int = const.DEFAULT_FRAMERATE
    keepalive: float = const.DEFAULT_TYPEWRITER_KEEPALIVE
    skip: key.KeyBinding | None = None


@dataclasses.dataclass(frozen=True)
class TextBoxSettings(TypewriterTextOptions):
    auto_scroll: float = 0
    advance_text: key.KeyBinding | None = None
    margins: Margins = dataclasses.field(default_factory=Margins)
    box_sprite: SpriteOptions = dataclasses.field(default_factory=SpriteOptions)
    indicator: SpriteOptions | None = None


@dataclasses.dataclass(frozen=True)
class ButtonOptions(SpriteOptions):
    text: str = ""
    hover_color: types.ColorValue = ""
    text_opts: TextOptions | None = None


@dataclasses.dataclass(frozen=True)
class MenuSettings(io.Configurable):
    buttons: List[ButtonOptions]
    # XXX: highlight topleft is used as an offset which
    # isn't clear given how other GameSprites behave
    highlight: SpriteOptions | None = None
