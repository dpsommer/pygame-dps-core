import logging
import pathlib

import pytest

import pygame_dps_core as pgcore

TEST_DIR = pathlib.Path(__file__).resolve().parent
TEST_RESOURCE_DIR = TEST_DIR / "resources"


@pytest.fixture(autouse=True, scope="session")
def init():
    pgcore.init(
        resource_dir=TEST_RESOURCE_DIR,
        game_name="test",
    )
