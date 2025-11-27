import functools
from typing import Dict, List

import pygame

from . import io, scenes
from .logs import logger

__keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()


class KeyBinding(io.Configurable):

    def __init__(
        self, *, key: str, mods: List[str] | None = None, toggle: bool = False
    ):
        self.key = key
        self.key_code = pygame.key.key_code(key)
        self.mods = functools.reduce(
            lambda x, k: x & pygame.key.key_code(k), mods or [], 0
        )
        self.toggle = toggle

    def is_pressed(self) -> bool:
        if not pygame.key.get_focused():
            return False
        mods_pressed = pygame.key.get_mods() & self.mods == self.mods
        key_pressed = __keys_pressed[self.key_code]
        return mods_pressed and key_pressed


__key_bindings: Dict[str, Dict[str, KeyBinding]] = {}


def _load(scene_name: str, bindings: Dict[str, KeyBinding]):
    for action, binding in bindings.items():
        __key_bindings[scene_name][action] = binding


def load_all_bindings(scene_bindings: Dict[str, Dict[str, KeyBinding]]):
    for scene_name, bindings in scene_bindings.items():
        _load(scene_name, bindings)


def is_key_pressed(action: str) -> bool:
    scene = scenes.get_active_scene()

    if scene.name not in __key_bindings:
        logger.error(f"No key bindings loaded for scene '{scene.name}'")
        return False
    if action not in __key_bindings[scene.name]:
        logger.error(f"No key bound for action '{action}' in scene '{scene.name}'")
        return False

    return __key_bindings[scene.name][action].is_pressed()


def update_pressed():
    global __keys_pressed
    __keys_pressed = pygame.key.get_pressed()


__all__ = [
    "KeyBinding",
    "is_key_pressed",
    "load_all_bindings",
    "update_pressed",
]
