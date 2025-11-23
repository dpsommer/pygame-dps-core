from typing import Any, List, Protocol, Sequence, Tuple

import pygame

# use type definitions from pygame._common

RGBOutput = Tuple[int, int, int]
RGBAOutput = Tuple[int, int, int, int]
ColorValue = pygame.Color | int | str | RGBOutput | RGBAOutput | Sequence[int]

Coordinate = Tuple[float, float] | Sequence[float] | pygame.Vector2

# implement sprite pyi sprite/group type protos
# XXX: move these and other type defs to a pyi file at some point?
_Group = pygame.sprite.AbstractGroup


class SupportsSprite(Protocol):
    @property
    def layer(self) -> int: ...
    @layer.setter
    def layer(self, value: int) -> None: ...

    # leave this as-is otherwise we'll get more incompatible type
    # errors from pyright when using as a type bound
    def __init__(self, *sprites) -> None: ...
    def add_internal(self, group: _Group) -> None: ...
    def remove_internal(self, group: _Group) -> None: ...
    def update(self, *args: Any, **kwargs: Any) -> None: ...
    def add(self, *groups: _Group) -> None: ...
    def remove(self, *groups: _Group) -> None: ...
    def kill(self) -> None: ...
    def alive(self) -> bool: ...
    def groups(self) -> List[_Group]: ...


class SpriteSupportsGroup(SupportsSprite, Protocol):
    rect: pygame.Rect
    image: pygame.Surface
