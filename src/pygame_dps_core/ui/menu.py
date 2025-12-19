from typing import List, Type

import pygame
from pygame.sprite import LayeredDirty

from . import settings, sprite
from .button import Button
from .container import Container


class Menu(Container):
    """Base class for in-game menus

    Args:
        screen (pygame.Surface): draw surface for rendering the menu
    """

    settings_type: Type[settings.MenuSettings] = settings.MenuSettings

    def __init__(self, settings: settings.MenuSettings, screen: pygame.Surface):
        super().__init__(screen)
        buttons = [Button(opts) for opts in settings.buttons]
        # need https://github.com/pygame/pygame/pull/4635 to be merged
        # to get rid of the pylance type assignment error here
        self.buttons: LayeredDirty[Button] = LayeredDirty(*buttons)  # type: ignore

    def _on_enter(self):
        self.dirty_all_sprites()
        super()._on_enter()

    def handle_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP | pygame.MOUSEMOTION:
                for i, button in enumerate(self.buttons):
                    button.handle_event(event)
                    if button.hovered or button.pressed:
                        self.selected = i
            case events.BUTTON_CLICKED:
                pass  # TODO: how do we get the button callback?
                # what are some options here?
                # we could assign a callback
            case pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.selected = 0 if not self.selected else self.selected + 1

    def update(self, dt: float):
        self.buttons.update(dt)

    def _draw(self) -> List[pygame.Rect]:
        rects = self.buttons.draw(self.screen)
        if self.selected and self.highlight:
            # XXX: group order may not match insertion order
            highlighted = self.buttons.sprites()[self.selected]
            pos = highlighted.rect.move(self.highlight.origin).topleft
            rects.append(
                self.screen.blit(self.highlight.image, pos, self.highlight.source_rect)
            )
        return rects

    def dirty_all_sprites(self):
        for btn in self.buttons:
            if btn.visible:
                btn.dirty = 1
