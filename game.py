# LEGO Story - Clase principal del juego
import pygame
from settings import *
from scenes import TitleScene, CutsceneScene, Level1Scene, DrBattleScene, VictoryScene


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = TitleScene()
        self.scene_name = 'title'

    def _load_scene(self, name):
        self.scene_name = name
        if name == 'title':
            self.current_scene = TitleScene()
        elif name == 'intro':
            self.current_scene = CutsceneScene(0)
        elif name == 'level1':
            self.current_scene = Level1Scene()
        elif name == 'droid_battle':
            self.current_scene = DrBattleScene()
        elif name == 'victory':
            self.current_scene = VictoryScene()

    def handle_events(self, events):
        for event in events:
            result = self.current_scene.handle_event(event)
            if result:
                self._load_scene(result)

    def update(self, dt):
        result = self.current_scene.update()
        if result:
            self._load_scene(result)

    def draw(self):
        self.current_scene.draw(self.screen)
