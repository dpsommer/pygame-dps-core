import dataclasses
from typing import Dict, Set, Type

from . import io


@dataclasses.dataclass
class KeyMapSettings(io.Configurable):
    pass  # TODO


class KeyMap(io.Loadable):

    settings_type: Type[KeyMapSettings] = KeyMapSettings

    def __init__(self, settings: KeyMapSettings):
        pass
