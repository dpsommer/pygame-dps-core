import pathlib
from typing import List

import pygame
from pygame.rect import Rect as Rect

import pygame_dps_core as pgcore

SRC_DIR = pathlib.Path(__file__).resolve().parent
RESOURCE_DIR = SRC_DIR.parent / "resources"


class TextExample(pgcore.Scene):

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.draw_group = pygame.sprite.LayeredUpdates()
        self.rect = self.screen.get_rect()
        self.writer = None

    def update(self, dt: float):
        pass

    def draw(self) -> List[Rect]:
        self.screen.fill("white")

        font = pygame.font.SysFont("arial", 20)
        opts = pgcore.TextOptions(font, "black", align=pgcore.Align.CENTER)
        spr = pgcore.text_sprite("Press Enter", opts, (10, 10))
        rects = [self.screen.blit(spr.image, spr.rect)]

        if self.writer is not None:
            try:
                self.draw_group, _ = next(self.writer)
                return rects + self.draw_group.draw(self.screen)
            except StopIteration:
                print("Finished writing")
                self.writer = None

        return rects

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                text_box = pgcore.TextBox.load(
                    settings_file="text_box.yml", screen=self.screen
                )
                text_box.add_text(
                    """A very long string to write in the text box.
It will take several panes to write out all this text!

Auto-scroll is enabled, so each text window will automatically continue
after the time elapses. It is set to 3 seconds.

To skip the text before that, press Enter once the text finishes writing.
"""
                )
                pgcore.new_scene(text_box)
            if event.key == pygame.K_RETURN:
                if self.writer is None:
                    self._new_writer()
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _new_writer(self):
        text = """Some long text to write to the screen.
It contains some line breaks.\nIt will be typed out based on
the configured text_speed that we pass to the typewriter
generator.
"""
        font = pygame.font.SysFont("arial", 18)
        opts = pgcore.TypewriterTextOptions(
            font=font,
            color="black",
            justify=True,
            align=pgcore.Align.CENTER,
            vertical_align=pgcore.VerticalAlign.CENTER,
            text_speed=5,
        )
        self.writer = pgcore.typewriter(text, opts, self.rect, self.draw_group)

    def dirty_all_sprites(self):
        pass


def run():
    pgcore.init(RESOURCE_DIR, "Text Example")
    game = pgcore.Game.load(settings_file="game.yml")
    game.run(TextExample(screen=game.draw_surface))


if __name__ == "__main__":
    run()
