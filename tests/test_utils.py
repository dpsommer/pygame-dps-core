import pytest

import pygame_dps_core as pgcore


@pytest.mark.parametrize(
    "path,expected",
    [
        (
            "C:\\\\Program Files\\Some Windows Path",
            "C:/Program Files/Some Windows Path",
        ),
        (
            "/home/my_user/.config/pytest/my_game",
            "/home/my_user/.config/pytest/my_game",
        ),
        (
            "/home/my_user/.config/pytest/my_game/assets\\image.png",
            "/home/my_user/.config/pytest/my_game/assets/image.png",
        ),
        (
            "C:\\\\Users\\myuser\\AppData\\Roaming\\MyGame\\Resources\\assets/image.png",
            "C:/Users/myuser/AppData/Roaming/MyGame/Resources/assets/image.png",
        ),
    ],
)
def test_normalize_path_str(path, expected):
    normalized_path = pgcore.normalize_path_str(path)
    assert str(normalized_path) == expected
