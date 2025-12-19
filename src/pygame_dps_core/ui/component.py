from pygame_dps_core.core import Signal

from . import sprite


class Component(sprite.GameSprite):

    focused: Signal
    unfocused: Signal

    mouse_entered: Signal
    mouse_exited: Signal

    def _input(self):
        pass

    def _unhandled_input(self):
        pass

    # focus
