import abc
import collections
import functools
import inspect
import uuid
from typing import Callable, Dict, List


class Signal:

    # holds a map of {ID}_{signal_name} to Signal objects.
    # we create a new Signal for each Signal property on a
    # GameObject instance so that each instance has its own
    # unique connections but shares a single event type
    _instances: Dict[str, "Signal"] = {}

    def __init__(self, obj: "GameObject"):
        self.obj = obj
        self._connections: List[Callable] = []

    def connect(self, fn: Callable, *args, **kwargs):
        self._connections.append(functools.partial(fn, *args, **kwargs))

    def emit(self, *args, **kwargs):
        # TODO: different types of connections
        [conn(*args, **kwargs) for conn in self._connections]

    @staticmethod
    def instance(obj: "GameObject", signal: str):
        key = f"{obj._id}_{signal}"
        if key in Signal._instances:
            return Signal._instances[key]
        instance = Signal(obj)
        Signal._instances[key] = instance
        return instance


class GameObjectMeta(abc.ABCMeta):

    _initialized = collections.defaultdict(bool)

    def __new__(mcls, name, bases, namespace, /, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        mcls._define_signals(cls)
        return cls

    @classmethod
    def _define_signals(mcls, cls):
        if not mcls._initialized[cls]:
            for var, annotation in inspect.get_annotations(cls).items():
                if issubclass(annotation, Signal):
                    # for each declared Signal, generate a @property getter
                    # that returns an instance of Signal keyed off the object's
                    # ID and the property name
                    fget = lambda self: Signal.instance(self._id, var)
                    setattr(cls, var, property(fget))
            mcls._initialized[cls] = True


class GameObject(metaclass=GameObjectMeta):

    def __init__(self, *args, **kwargs):
        self._id = uuid.uuid4()

    def __hash__(self) -> int:
        return hash(self._id)
