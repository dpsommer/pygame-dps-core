from typing import Dict, List

import pygame

from pygame_dps_core import core, io, types

from . import settings


class GameSprite(core.Node, pygame.sprite.WeakDirtySprite):

    draw: core.Signal
    visibility_changed: core.Signal

    def __init__(self, opts: settings.SpriteOptions, screen: pygame.Surface):
        super().__init__()
        self.screen = screen

        self._pending_update = False

        self._layer = opts.layer
        self.origin = opts.topleft
        image_size = (opts.width, opts.height)
        self.image = opts.image if opts.image else pygame.Surface(image_size)

        # source image from its bounding rect
        # (inner rect at first non-transparent pixels)
        self.source_rect = self.image.get_bounding_rect()
        self.rect = self.image.get_rect()
        self.rect.update(self.origin, self.source_rect.size)

    def _set_visible(self, val: int):
        super()._set_visible(val)
        self.visibility_changed.emit(visible=val)

    def queue_redraw(self):
        if self._pending_update:
            return

        self._pending_update = True
        self._redraw()

    def _redraw(self):
        self.dirty = 1

    def _draw(self):
        # TODO: this method needs to be called when
        # draw group draw() is called
        self._pending_update = False
        self.draw.emit()

    def update(self, dt: float):
        self._update(dt)

    def _reset(self):
        self.rect.update(self.origin, self.source_rect.size)


# TODO:
class Animation(pygame.sprite.WeakSprite):

    def __init__(self, opts: settings.AnimationOptions, frames: List[pygame.Surface]):
        self.repeat = opts.repeat
        self.frames = frames
        self.frames_inverted = [pygame.transform.flip(f, True, False) for f in frames]
        self.image = frames[0]
        self.rect = self.image.get_rect()

    def play(self, pos: types.Coordinate):
        pass


class SpriteSheet(io.Loadable):

    def __init__(self, opts: settings.SpriteSheetSettings):
        self.sprite_sheet = opts.sprite_sheet
        self.sprite_width = opts.sprite_width
        self.sprite_height = opts.sprite_height
        self.animations = self._load_animations(opts.animation_opts)

    def _load_animations(
        self, animation_opts: List[settings.AnimationOptions]
    ) -> Dict[str, Animation]:
        animations = {}
        # each row in the sprite sheet represents an animation
        for i, opts in enumerate(animation_opts):
            frames = self._split_frames(i)
            animations[opts.name] = Animation(opts, frames)
        return animations

    def _split_frames(self, idx: int) -> List:
        frames = []
        for i in range(self.sprite_sheet.get_width() // self.sprite_width):
            topleft = (i * self.sprite_width, idx * self.sprite_height)
            wh = (self.sprite_width, self.sprite_height)
            frame = self.sprite_sheet.subsurface(topleft, wh)
            # create a mask of the frame and check if it contains any
            # non-transparent pixels. if not, break and return
            mask = pygame.mask.from_surface(frame)
            if mask.count() == 0:
                break
            frames.append(frame)
        return frames
