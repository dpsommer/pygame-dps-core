import collections
import dataclasses
import enum
import functools
import itertools
from typing import Generator, Iterable, List, Type

import pygame

from . import const, io, keys, scenes, sprites, types


class Align(enum.Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(enum.Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


@dataclasses.dataclass
class _PreparedText:
    line: str
    dest: types.Coordinate | pygame.Rect


@dataclasses.dataclass
class Margins:
    top: int = 0
    left: int = 0
    right: int = 0
    bottom: int = 0

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        margin_rect = rect.move(self.left, self.top)
        margin_rect.inflate_ip(-(self.left + self.right), -(self.top + self.bottom))
        return margin_rect


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
    advance_text: keys.KeyBinding | None = None
    margins: Margins = dataclasses.field(default_factory=Margins)
    sprite_opts: sprites.SpriteOptions = dataclasses.field(
        default_factory=sprites.SpriteOptions
    )


# TODO: wrap this in a controller so that cache settings are configurable
@functools.lru_cache()
def create_text_surface(text: str, opts: TextOptions) -> pygame.Surface:
    """Renders and caches text surfaces to be drawn to the screen"""
    return opts.font.render(text, opts.antialias, opts.color, opts.bg_color)


def text_sprite(
    text: str, opts: TextOptions, dest: types.Coordinate | pygame.Rect, layer: int = 0
) -> sprites.GameSprite:
    img = create_text_surface(text, opts)
    text_w, text_h = img.get_size()

    if isinstance(dest, pygame.Rect):
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

    return sprites.GameSprite(
        opts=sprites.SpriteOptions(dest, text_w, text_h, img, layer)
    )


def multiline_text(
    text: str,
    opts: TextOptions,
    dest: pygame.Rect,
    layer: int = 0,
) -> List[sprites.GameSprite]:
    prepared_texts = _prepare_multiline(text, opts, dest)
    return [text_sprite(prep.line, opts, prep.dest, layer) for prep in prepared_texts]


def _prepare_multiline(
    text: str,
    opts: TextOptions,
    rect: pygame.Rect,
) -> collections.deque[_PreparedText]:
    w, h = rect.size
    line_height = opts.font.get_linesize()
    prepared_texts: collections.deque[_PreparedText] = collections.deque()

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
    text: str | Iterable[_PreparedText],
    opts: TypewriterTextOptions,
    dest: pygame.Rect,
    group: pygame.sprite.LayeredUpdates | None = None,
) -> Generator[pygame.sprite.LayeredUpdates, None, None]:
    group = group or pygame.sprite.LayeredUpdates()
    text_layer = 0

    if len(group.sprites()) > 0:
        text_layer = group.get_top_layer() + 1

    if isinstance(text, str):
        if opts.font.size(text)[0] > dest.w:
            prepared_texts = _prepare_multiline(text, opts, dest)
        else:
            prepared_texts = collections.deque((_PreparedText(text, dest),))
    else:
        prepared_texts = collections.deque(text)

    text_sprites = [
        text_sprite(prep.line, opts, prep.dest, text_layer) for prep in prepared_texts
    ]

    text_speed = pygame.math.clamp(opts.text_speed, 0, const.MAX_TEXT_SPEED)
    if text_speed > 0:
        tmp_group = group.copy()
        # store prepared_texts and line indices and track the
        # number of frames to wait to print each character
        # based on configured framerate and text speed
        char_idx = step_frames = 0
        current = prepared_texts.popleft()
        line = ""

        while prepared_texts or len(line) < len(current.line):
            # remove the currently typing line from the group
            tmp_group.remove_sprites_of_layer(text_layer + 1)

            if len(line) == len(current.line):
                tmp_group.add(text_sprite(current.line, opts, current.dest, text_layer))
                current = prepared_texts.popleft()
                line = ""
                char_idx = 0

            if step_frames == 0:
                line += current.line[char_idx]
                char_idx += 1
                step_frames = opts.framerate // (text_speed * 6)
            step_frames -= 1

            # write the typing line to its own layer so we can replace it
            tmp_group.add(text_sprite(line, opts, current.dest, text_layer + 1))
            yield tmp_group

    group.add(*text_sprites)

    keepalive = opts.keepalive * opts.framerate
    while keepalive > 0:
        yield group
        keepalive -= 1


class TextBox(scenes.Scene):

    settings_type: Type[TextBoxSettings] = TextBoxSettings

    def __init__(self, settings: TextBoxSettings, screen: pygame.Surface):
        super().__init__(screen)
        self.settings = settings
        self.advance_text = settings.advance_text

        self.text_box = sprites.GameSprite(opts=settings.sprite_opts)
        self.text_rect = self.text_box.rect
        if self.settings.margins is not None:
            self.text_rect = self.settings.margins.apply(self.text_box.rect)

        self.draw_group = pygame.sprite.LayeredUpdates(self.text_box)  # type: ignore
        self._text_blocks = collections.deque()
        self.writer = None

    def add_text(self, text: str):
        prep = _prepare_multiline(text, self.settings, self.text_rect)
        lines_per_block = self.text_rect.h // self.settings.font.get_linesize()
        self._text_blocks.extend(itertools.batched(prep, lines_per_block))

    def _new_writer(self, text: str):
        self.writer = typewriter(
            text, self.settings, self.text_box.rect, self.draw_group
        )

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        if self.settings.auto_scroll == 0:
            if self.advance_text is not None and self.advance_text.is_pressed():
                if not self._text_blocks:
                    scenes.end_current_scene()
                self._new_writer(self._text_blocks.popleft())

        if self.writer is not None:
            try:
                self.draw_group = next(self.writer)
            except StopIteration:
                self.writer = None

        self.draw_group.update()

    def draw(self) -> List[pygame.Rect]:
        return self.draw_group.draw(self.screen)

    def dirty_all_sprites(self):
        for sprite in self.draw_group:
            sprite.dirty = 1
