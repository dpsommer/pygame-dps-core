import dataclasses

import pygame

from pygame_dps_core.core import Signal
from pygame_dps_core.key import KeyBinding

from . import settings, sprite, text


class BaseButton(sprite.GameSprite):
    """Clickable sprite button

    Args:
        opts (ButtonOptions): configuration options for the button
        on_click (Callable): on-click callback
    """

    button_down: Signal
    button_up: Signal
    button_pressed: Signal

    hovered: bool = False
    pressed: bool = False
    enabled: bool = True
    keep_pressed_outside: bool = True

    key_binding: KeyBinding | None = None

    def __init__(self, opts: settings.ButtonOptions):
        super().__init__(opts)

    def _pressed(self):
        self.button_pressed.emit()

    def _notification(self, code: int):
        match code:
            case 1:
                pass

    def _input(self, event: pygame.event.Event):
        pass

    def _unhandled_input(self, event: pygame.event.Event):
        pass

    # XXX: handling mouse events in the button class is not ideal
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            if self.pressed:
                if self.rect.collidepoint(event.pos):
                    pygame.event.post(self._click_event())
                self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)


class Button(BaseButton):

    def __init__(self, opts: settings.ButtonOptions):
        super().__init__(opts)
        self.text = opts.text
        self.text_opts = opts.text_opts
        if self.text_opts is not None:
            self.hover_opts = dataclasses.replace(
                self.text_opts, color=opts.hover_color
            )

    def update(self, dt: float):
        if self.text and self.text_opts is not None:
            opts = self.hover_opts if self.hovered else self.text_opts
            sprite = text.text_sprite(self.text, opts, self.rect.move(0, 0))
            self.image.blit(sprite.image, sprite.rect)
