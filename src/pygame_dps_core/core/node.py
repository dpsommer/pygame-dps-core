from typing import List, Set

import pygame

from . import base


class Node(base.GameObject):

    child_entered: base.Signal
    child_exited: base.Signal

    node_entered: base.Signal
    node_exited: base.Signal

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children: Set[Node] = set()
        self._parent: Node | None = None

    @property
    def children(self) -> List["Node"]:
        return list(self._children)

    @property
    def parent(self) -> "Node | None":
        return self._parent

    @parent.setter
    def parent(self, parent: "Node"):
        self._parent = parent

    def _on_enter(self):
        pass

    def _on_exit(self):
        pass

    def _update(self, dt: float):
        pass

    def _notification(self, code: int):
        pass

    def _input(self, event: pygame.event.Event):
        pass

    def _unhandled_input(self, event: pygame.event.Event):
        pass

    def add_child(self, child: "Node"):
        """Adds the given Node as a child of this object

        Args:
            child (Node): the child object to add
        """
        self._children.add(child)
        child.parent = self
        child._on_enter()

        # send enter signals
        child.node_entered.emit()
        self.child_entered.emit(node=child)

    def remove_child(self, child: "Node"):
        """Removes the given child from this object's tree

        Args:
            child (Node): the child object to remove

        Raises:
            KeyError: if the given Node isn't a child of this object
        """
        child._on_exit()
        self._children.remove(child)

        # send exit signals
        child.node_exited.emit()
        self.child_exited.emit(node=child)
