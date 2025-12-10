import dataclasses
from typing import Any, Dict, List, Type

import pygame

from . import scenes, text


@dataclasses.dataclass(frozen=True)
class DiagnosticsSettings(text.TextOptions):
    margin: int = 2


class Diagnostics(scenes.Scene):

    settings_type: Type[DiagnosticsSettings] = DiagnosticsSettings

    def __init__(self, settings: DiagnosticsSettings, screen: pygame.Surface):
        super().__init__(screen)
        self.diagnostics: Dict[str, Any] = {}
        self._active_scene: scenes.Scene
        self.opts = settings
        self.margin = settings.margin

    def _on_enter(self):
        super()._on_enter()
        self._active_scene = scenes.get_active_scene()

    def add(self, name: str, value: Any):
        self.diagnostics[name] = value

    def draw(self) -> List[pygame.Rect]:
        rects = self._active_scene.draw()

        col_width = 0
        _, window_height = pygame.display.get_window_size()
        line_height = self.opts.font.get_linesize()

        for i, diag in enumerate(self.diagnostics.items()):
            name, val = diag
            if type(val) is pygame.Rect:
                val = val.center

            max_in_col = int(
                ((window_height - (self.margin * 2)) / (line_height + self.margin))
            )
            col, row = divmod(i, max_in_col)
            x = (col * col_width) + self.margin
            y = (row * line_height) + self.margin

            img = text.draw_text(f"{name}: {val}", self.opts, self.screen, (x, y))
            w, _ = img.get_size()
            col_width = max(col_width, w)

        return rects

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_F12, pygame.K_ESCAPE):
                scenes.end_current_scene()
                return
        self._active_scene.handle_event(event)

    def update(self, dt: float):
        self._active_scene.update(dt)

    def dirty_all_sprites(self):
        self._active_scene.dirty_all_sprites()

    def _reset(self):
        pass  # no-op
