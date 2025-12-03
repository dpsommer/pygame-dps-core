import collections
import functools
from typing import Dict, List

import pygame

from . import io

__keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
__keys_toggled: Dict[int, bool] = collections.defaultdict(bool)


class KeyBinding(io.Configurable):

    def __init__(
        self, *, key: str, mods: List[str] | None = None, toggle: bool = False
    ):
        self.key = key
        self.key_code = pygame.key.key_code(key)
        mod_keys = [pygame.key.key_code(k) for k in mods or []]
        self.mods = functools.reduce(lambda x, k: x & k, mod_keys, 0)
        self.toggle = toggle

    def is_pressed(self) -> bool:
        # toggle takes priority even when the window loses focus
        if self.toggle:
            return __keys_toggled[self.key_code]
        if not pygame.key.get_focused():
            return False
        mods_pressed = pygame.key.get_mods() & self.mods == self.mods
        key_pressed = __keys_pressed[self.key_code]
        return mods_pressed and key_pressed


__key_bindings: Dict[str, KeyBinding] = {}


def is_key_pressed(action: str, default: int | None = None) -> bool:
    if action in __key_bindings:
        return __key_bindings[action].is_pressed()
    # TODO: gamepad detection and impl
    if default is not None:
        return __keys_pressed[default]
    return False


def load_bindings(bindings: Dict[str, KeyBinding]):
    __key_bindings.update(bindings)


def update_pressed():
    global __keys_pressed
    __keys_pressed = pygame.key.get_pressed()


def flip_toggle(keys: int, value: bool | None = None):
    __keys_toggled[keys] = value if value is not None else __keys_toggled[keys]


__all__ = [
    "KeyBinding",
    "flip_toggle",
    "is_key_pressed",
    "load_bindings",
]
