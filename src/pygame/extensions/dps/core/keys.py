import collections
import functools
from typing import Dict, List

import pygame

from . import io


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
            return key.keys_toggled[self.key_code]
        if not pygame.key.get_focused():
            return False
        mods_pressed = pygame.key.get_mods() & self.mods == self.mods
        key_pressed = key.keys_pressed[self.key_code]
        return mods_pressed and key_pressed


class __KeyController:

    def __init__(self):
        self.key_bindings: Dict[str, KeyBinding] = {}
        self.keys_pressed: pygame.key.ScancodeWrapper
        self.keys_toggled: Dict[int, bool] = collections.defaultdict(bool)

    def update(self):
        self.keys_pressed = pygame.key.get_pressed()

    # XXX: rename this to e.g. is_binding_pressed?
    def is_pressed(self, action: str, default: int | None = None) -> bool:
        if action in self.key_bindings:
            return self.key_bindings[action].is_pressed()
        # TODO: gamepad detection and impl
        if default is not None:
            return self.keys_pressed[default]
        return False

    def load_bindings(self, bindings: Dict[str, KeyBinding]):
        self.key_bindings.update(bindings)

    def flip_toggle(self, keys: int, value: bool | None = None):
        self.keys_toggled[keys] = (
            value if value is not None else self.keys_toggled[keys]
        )


key = __KeyController()


__all__ = [
    "KeyBinding",
    "key",
]
