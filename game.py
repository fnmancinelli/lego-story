# LEGO Story - Clase principal del juego
import pygame
from settings import *
from scenes import (TitleScene, CharSelectScene, CutsceneScene,
                    Level1Scene, DrBattleScene, VictoryScene)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.selected_char = OBI_WAN
        self.current_scene = TitleScene()
        self.scene_name = 'title'

    def _load_scene(self, name):
        self.scene_name = name
        if name == 'title':
            self.current_scene = TitleScene()
        elif name == 'char_select':
            self.current_scene = CharSelectScene()
        elif name == 'intro':
            self.current_scene = CutsceneScene(0, self.selected_char)
        elif name == 'level1':
            self.current_scene = Level1Scene(self.selected_char)
        elif name == 'droid_battle':
            self.current_scene = DrBattleScene(self.selected_char)
        elif name == 'victory':
            self.current_scene = VictoryScene(self.selected_char)

    def handle_events(self, events):
        for event in events:
            result = self.current_scene.handle_event(event)
            if result is None:
                continue
            # La selección de personaje devuelve una tupla
            if isinstance(result, tuple) and result[0] == 'char_selected':
                self.selected_char = result[1]
                self._load_scene('intro')
            else:
                self._load_scene(result)

    def update(self, dt):
        result = self.current_scene.update()
        if result:
            self._load_scene(result)

    def draw(self):
        self.current_scene.draw(self.screen)
