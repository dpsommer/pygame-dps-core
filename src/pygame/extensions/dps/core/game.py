import collections
import dataclasses
from typing import Dict, Type

import pygame

from . import _conf, io, keys, scenes, types


@dataclasses.dataclass
class GameSettings(io.Configurable):
    game_width: int
    game_height: int

    screen_width: int
    screen_height: int
    fullscreen: bool
    framerate: int

    key_map: Dict[str, keys.KeyBinding] = dataclasses.field(default_factory=dict)
    icon: pygame.Surface | None = None


class Game(io.Loadable):
    """Game runtime class

    Controls display settings and rendering, handles system events, and
    triggers per-frame tick.

    Args:
        settings (GameSettings): game configuration settings
    """

    settings_type: Type[GameSettings] = GameSettings

    def __init__(self, settings: GameSettings):
        screen_size = (settings.screen_width, settings.screen_height)
        flags = pygame.RESIZABLE | (settings.fullscreen and pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode(screen_size, flags=flags)
        self.rect = self.screen.get_rect()

        pygame.display.set_caption(_conf.GAME.name)
        if settings.icon is not None:
            pygame.display.set_icon(settings.icon)

        # create a separate draw surface for all scenes to draw to. the draw
        # surface maintains its size and is scaled to match the screen
        game_size = (settings.game_width, settings.game_height)
        self._draw_surface = pygame.Surface(game_size)

        self.clock = pygame.time.Clock()
        self.framerate = settings.framerate

        # action strings mapped to key bindings are loaded into a global lookup
        keys.load_bindings(settings.key_map)
        # keep our own track of key presses on KEYDOWN/KEYUP so that we can set
        # key toggles correctly if repeat is enabled
        self._pressed = collections.defaultdict(bool)
        self._running = False

    def run(self, main_scene: scenes.Scene):
        pygame.init()
        scenes.new_scene(main_scene)
        self._rescale()
        self._running = True

        while self._running:
            self._handle_events()
            self._tick()
            self._render()

        pygame.quit()

    def _handle_events(self):
        scene = scenes.get_active_scene()

        for event in pygame.event.get():
            # handle system-level events. all events are still passed to the
            # scene in case further processing is needed
            match event.type:
                case pygame.QUIT:
                    self._running = False
                case pygame.WINDOWRESIZED | pygame.WINDOWSIZECHANGED:
                    self._rescale()
                case pygame.WINDOWMAXIMIZED:
                    pygame.display.toggle_fullscreen()
                    self._rescale()
                case pygame.KEYDOWN:
                    # set our own key pressed value on down/up so toggle
                    # will still work as expected if repeat is enabled
                    if not self._pressed[event.key]:
                        keys.flip_toggle(event.key & pygame.key.get_mods())
                        self._pressed[event.key] = True
                case pygame.KEYUP:
                    self._pressed[event.key] = False
                case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP | pygame.MOUSEMOTION:
                    # adjust the position of mouse events by the window scale factor
                    event.pos = self._scale_pos(event.pos)
            scene.handle_event(event)

    def _render(self):
        scene = scenes.get_active_scene()
        scene.draw()

        scale_factor = self.get_scale_factor()
        scaled = pygame.transform.scale_by(self._draw_surface, scale_factor)
        scaled_rect = scaled.get_rect()
        scaled_rect.center = self.screen.get_rect().center

        self.screen.blit(scaled, scaled_rect)
        pygame.display.update(scaled_rect)

    def _tick(self):
        dt = self.clock.tick(self.framerate) / 1000
        # run pygame.key.get_pressed() once per tick
        keys.update_pressed()
        scene = scenes.get_active_scene()
        scene.tick(dt)

    def _rescale(self):
        self.rect = self.screen.get_rect()
        # mark all sprites in the scene dirty so everything gets redrawn on resize
        scenes.get_active_scene().dirty_all_sprites()
        pygame.display.update()

    def _scale_pos(self, pos: types.Coordinate) -> types.Coordinate:
        x, y = pos
        scale_factor = self.get_scale_factor()
        w, h = self._draw_surface.get_size()
        x_offset = (self.screen.get_width() - (w * scale_factor)) / 2
        y_offset = (self.screen.get_height() - (h * scale_factor)) / 2
        return ((x - x_offset) / scale_factor, (y - y_offset) / scale_factor)

    def get_scale_factor(self) -> float:
        game_width, game_height = self._draw_surface.get_size()
        width_scale = self.screen.get_width() / game_width
        height_scale = self.screen.get_height() / game_height
        return min(width_scale, height_scale)
