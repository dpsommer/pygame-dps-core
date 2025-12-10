import dataclasses
import enum
import functools
from collections import deque
from typing import Generator, List, Type

import pygame

from . import const, io, scenes, types


class Align(enum.Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(enum.Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


@dataclasses.dataclass(frozen=True)
class TextOptions(io.Configurable):
    font: pygame.font.Font
    color: types.ColorValue
    bg_color: types.ColorValue | None = None
    antialias: bool = True
    justify: bool = False
    align: Align = dataclasses.field(default=Align.LEFT)
    vertical_align: VerticalAlign = dataclasses.field(default=VerticalAlign.TOP)


@dataclasses.dataclass(frozen=True)
class TypewriterTextOptions(TextOptions):
    text_speed: int = const.DEFAULT_TEXT_SPEED
    framerate: int = const.DEFAULT_FRAMERATE
    keepalive: int = const.DEFAULT_TYPEWRITER_KEEPALIVE


@dataclasses.dataclass(frozen=True)
class TextBoxSettings(TypewriterTextOptions):
    auto_scroll: int = 0


@dataclasses.dataclass
class _PreparedText:
    line: str
    dest: types.Coordinate | pygame.Rect


# TODO: wrap this in a controller so that cache settings are configurable
@functools.lru_cache()
def create_text_surface(text: str, opts: TextOptions) -> pygame.Surface:
    """Renders and caches text surfaces to be drawn to the screen"""
    return opts.font.render(text, opts.antialias, opts.color, opts.bg_color)


def draw_text(
    text: str,
    opts: TextOptions,
    surf: pygame.Surface,
    dest: types.Coordinate | pygame.Rect,
) -> pygame.Surface:
    img = create_text_surface(text, opts)

    if isinstance(dest, pygame.Rect):
        text_w, text_h = img.get_size()
        dx, dy = dest.topleft

        if opts.align is Align.CENTER:
            dx = dest.centerx - (text_w / 2)
        elif opts.align is Align.RIGHT:
            dx = dest.right - text_w

        if opts.vertical_align is VerticalAlign.CENTER:
            dy = dest.centery - (text_h / 2)
        elif opts.vertical_align is VerticalAlign.BOTTOM:
            dy = dest.bottom - text_h

        dest = (dx, dy)

    surf.blit(img, dest)
    return img


def draw_multiline_text(
    text: str, opts: TextOptions, surf: pygame.Surface, dest: pygame.Rect | None = None
) -> List[pygame.Surface]:
    if dest is None:
        dest = surf.get_rect()
    prepared_texts = _prepare_multiline(text, opts, dest)
    return [draw_text(prep.line, opts, surf, prep.dest) for prep in prepared_texts]


def _prepare_multiline(
    text: str, opts: TextOptions, rect: pygame.Rect
) -> deque[_PreparedText]:
    w, h = rect.size
    line_height = opts.font.get_linesize()
    prepared_texts: deque[_PreparedText] = deque()

    if opts.justify:
        lines = _split_and_justify(text, opts.font, rect)
    else:
        lines = text.splitlines()

    y_margin = 0
    if opts.vertical_align is VerticalAlign.CENTER:
        y_margin = (h - (len(lines) * line_height)) // 2
    elif opts.vertical_align is VerticalAlign.BOTTOM:
        y_margin = h - (len(lines) * line_height)

    for i, line in enumerate(lines):
        y = (i * line_height) + y_margin
        line_rect = pygame.Rect(rect.left, y, w, line_height)
        prepared_texts.append(_PreparedText(line=line, dest=line_rect))

    return prepared_texts


def _split_and_justify(
    text: str, font: pygame.font.Font, rect: pygame.Rect
) -> List[str]:
    lines = []
    line = ""
    line_space = rect.w

    for word in text.split():
        word = f"{word} "
        text_width, _ = font.size(word)
        if text_width > line_space:
            lines.append(line)
            line = ""
            line_space = rect.w
        line += word
        line_space -= text_width

    lines.append(line)
    return lines


def typewriter(
    text: str,
    opts: TypewriterTextOptions,
    surf: pygame.Surface,
    dest: pygame.Rect | None = None,
) -> Generator[List[pygame.Surface], None, None]:
    if dest is None:
        dest = surf.get_rect()

    if opts.font.size(text)[0] > dest.w:
        prepared_texts = _prepare_multiline(text, opts, dest)
    else:
        prepared_texts = deque()
        prepared_texts.append(_PreparedText(text, dest))

    if opts.text_speed > 0:
        visible: List[_PreparedText] = []
        current = prepared_texts.popleft()
        line = ""
        i = 0
        # number of frames to wait to print each character
        # based on configured framerate and text speed
        step_frames = 0

        while prepared_texts or len(line) < len(current.line):
            if len(line) == len(current.line):
                visible.append(current)
                current = prepared_texts.popleft()
                line = ""
                i = 0

            if step_frames == 0:
                line += current.line[i]
                i += 1
                step_frames = opts.framerate // (opts.text_speed * 6)
            step_frames -= 1

            drawn = [draw_text(p.line, opts, surf, p.dest) for p in visible]
            drawn.append(draw_text(line, opts, surf, current.dest))
            yield drawn

        visible.append(current)
        prepared_texts = visible

    keepalive = opts.keepalive * opts.framerate
    while keepalive > 0:
        yield [draw_text(prep.line, opts, surf, prep.dest) for prep in prepared_texts]
        keepalive -= 1


# TODO: overlay scene that draws a scrollable text box with the given text
class TextBox(scenes.Scene):

    settings_type: Type[TextBoxSettings] = TextBoxSettings

    def __init__(self, settings: TextBoxSettings, screen: pygame.Surface):
        super().__init__(screen)
        self.text_speed = pygame.math.clamp(
            settings.text_speed, 0, const.MAX_TEXT_SPEED
        )
