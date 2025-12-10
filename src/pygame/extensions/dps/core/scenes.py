import abc
from collections import deque
from typing import List

import pygame

from . import io


class Scene(io.Loadable, abc.ABC):
    """Defines methods for game scenes

    Args:
        screen (pygame.Surface): draw surface for rendering the scene
    """

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        # setup default background as just a black screen
        self.background = pygame.Surface(screen.get_size())

    def _on_enter(self):
        # draw to the screen once when the scene is loaded
        # FIXME: need a way to set background coords
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

    @abc.abstractmethod
    def draw(self) -> List[pygame.Rect]:
        pass

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    @abc.abstractmethod
    def update(self, dt: float):
        pass

    @abc.abstractmethod
    def dirty_all_sprites(self):
        pass

    def reset(self):
        # dirty sprites after update so they are
        # updated when we re-enter the scene
        self.dirty_all_sprites()


class __SceneController:

    def __init__(self) -> None:
        self.scenes: deque[Scene] = deque()

    def get_active_scene(self) -> Scene:
        """Returns the currently active scene"""
        if not self.scenes:
            raise pygame.error("No active scene!")
        return self.scenes[0]

    def new_scene(self, scene: Scene):
        """Starts a new scene as the active scene"""
        scene._on_enter()
        self.scenes.appendleft(scene)

    def end_current_scene(self) -> Scene:
        """Ends the currently active scene and returns the next in the stack"""
        ending_scene = self.scenes.popleft()
        ending_scene.reset()
        active_scene = self.get_active_scene()
        active_scene._on_enter()
        return active_scene


scene = __SceneController()


__all__ = [
    "Scene",
    "scene",
]
