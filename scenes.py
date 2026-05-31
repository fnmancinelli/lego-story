# LEGO Story - Escenas del juego
import pygame
import random
import math
from settings import *
from draw_utils import (draw_background, draw_lego_brick, draw_hud,
                        draw_minifigure, draw_droid, draw_lego_piece,
                        draw_gold_brick, lighter, darker)
from entities import Platform, Player, Stormtrooper, LegoPiece, GoldBrick, FlyingStud


# ──────────────────────────────────────────────────────
#  PANTALLA DE TÍTULO
# ──────────────────────────────────────────────────────
class TitleScene:
    def __init__(self):
        self.font_title = pygame.font.SysFont('Impact', 72)
        self.font_sub   = pygame.font.SysFont('Arial Black', 22)
        self.font_hint  = pygame.font.SysFont('Arial', 16)
        self.frame = 0
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(120)]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return 'char_select'
        return None

    def update(self):
        self.frame += 1

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        draw_lego_brick(surf, 0, 500, W, 100, DARK_GREY)

        # Personajes en el título (escala 1.6 ya por defecto en draw_minifigure)
        chars = [(160, 500, OBI_WAN, 1), (860, 500, DARTH_VADER, -1),
                 (510, 505, MUERTE_NEGRA, 1)]
        for cx, cy, ct, d in chars:
            state = 'idle' if ct == MUERTE_NEGRA else 'walk'
            draw_minifigure(surf, cx, cy, ct, d, state, self.frame)

        # Sables cruzados
        glow = int(abs(math.sin(self.frame * 0.05)) * 40)
        ix, iy = W//2, 435
        pygame.draw.line(surf, (80+glow, 80+glow, 255), (160+26, 468), (ix, iy), 5)
        pygame.draw.line(surf, (255, 40+glow, 40+glow), (860-26, 468), (ix, iy), 5)
        pygame.draw.circle(surf, WHITE, (ix, iy), 5 + glow//20)

        _draw_lego_text(surf, self.font_title, "LEGO",  W//2, 120, GOLD,  BLACK)
        _draw_lego_text(surf, self.font_title, "STORY", W//2, 205, RED,   BLACK)

        sub = self.font_sub.render("La Alianza Imposible", True, WHITE)
        surf.blit(sub, sub.get_rect(center=(W//2, 300)))

        if (self.frame // 30) % 2 == 0:
            hint = self.font_hint.render("Presioná ENTER para comenzar", True, YELLOW)
            surf.blit(hint, hint.get_rect(center=(W//2, 560)))

        ctrl = self.font_hint.render(
            "Flechas/WASD: mover   ESPACIO: saltar   Z: sable   X: Fuerza", True, GREY)
        surf.blit(ctrl, ctrl.get_rect(center=(W//2, 582)))


# ──────────────────────────────────────────────────────
#  SELECCIÓN DE PERSONAJE
# ──────────────────────────────────────────────────────
class CharSelectScene:
    CHARACTERS = [
        {
            'id': OBI_WAN,
            'name': 'Obi-Wan Kenobi',
            'title': 'Maestro Jedi',
            'saber': 'Azul',
            'force': 10,
            'speed': 7,
            'jump': 7,
            'desc': 'Maestro en la Fuerza,\nexperiencia y sabiduría.',
        },
        {
            'id': LUKE,
            'name': 'Luke Skywalker',
            'title': 'El Último Jedi',
            'saber': 'Verde',
            'force': 8,
            'speed': 8,
            'jump': 9,
            'desc': 'Ágil y valiente.\nSalto potenciado por la Fuerza.',
        },
        {
            'id': YODA,
            'name': 'Maestro Yoda',
            'title': 'Gran Maestro Jedi',
            'saber': 'Verde',
            'force': 10,
            'speed': 6,
            'jump': 8,
            'desc': 'Pequeño pero el más\npoderoso en la Fuerza.',
        },
        {
            'id': DARTH_VADER,
            'name': 'Darth Vader',
            'title': 'Señor Sith',
            'saber': 'Rojo',
            'force': 10,
            'speed': 7,
            'jump': 6,
            'desc': 'Aliado por necesidad.\nFuerza Oscura devastadora.',
        },
    ]

    def __init__(self):
        self.selected = 0
        self.frame = 0
        self.font_big   = pygame.font.SysFont('Impact', 38)
        self.font_title = pygame.font.SysFont('Arial Black', 22)
        self.font_med   = pygame.font.SysFont('Arial Black', 16)
        self.font_sm    = pygame.font.SysFont('Arial', 14)
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(100)]
        self.anim_frames = [0] * len(self.CHARACTERS)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(self.CHARACTERS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(self.CHARACTERS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return ('char_selected', self.CHARACTERS[self.selected]['id'])
        return None

    def update(self):
        self.frame += 1
        for i in range(len(self.CHARACTERS)):
            self.anim_frames[i] += 1

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        # Título
        _draw_lego_text(surf, self.font_big, "ELIGE TU PERSONAJE", W//2, 45, YELLOW, BLACK)

        n = len(self.CHARACTERS)
        card_w = 200
        spacing = (W - card_w * n) // (n + 1)

        for i, char in enumerate(self.CHARACTERS):
            cx = spacing + i * (card_w + spacing) + card_w // 2
            selected = (i == self.selected)

            # Tarjeta de fondo
            card_rect = pygame.Rect(cx - card_w//2, 80, card_w, 340)
            card_color = (20, 30, 60) if not selected else (40, 60, 120)
            border_color = YELLOW if selected else GREY
            pygame.draw.rect(surf, card_color, card_rect, border_radius=10)
            pygame.draw.rect(surf, border_color, card_rect,
                             3 if selected else 1, border_radius=10)

            if selected:
                # Brillo de selección
                glow_surf = pygame.Surface((card_w+20, 360), pygame.SRCALPHA)
                glow_a = int(abs(math.sin(self.frame*0.08)) * 40 + 20)
                pygame.draw.rect(glow_surf, (*YELLOW, glow_a),
                                 (0, 0, card_w+20, 360), border_radius=12)
                surf.blit(glow_surf, (cx - card_w//2 - 10, 78))

            # Personaje (más grande si está seleccionado)
            char_scale = 1.7 if selected else 1.4
            char_y = 235
            bob = int(math.sin(self.anim_frames[i] * 0.06) * 4) if selected else 0
            draw_minifigure(surf, cx, char_y + bob,
                            char['id'], 1, 'idle' if not selected else 'walk',
                            self.anim_frames[i], scale=char_scale)

            # Nombre del personaje
            name_c = YELLOW if selected else WHITE
            n_surf = self.font_med.render(char['name'], True, name_c)
            surf.blit(n_surf, n_surf.get_rect(center=(cx, 255)))

            # Título
            t_surf = self.font_sm.render(char['title'], True, GREY)
            surf.blit(t_surf, t_surf.get_rect(center=(cx, 272)))

            # Stats (barras)
            if selected:
                stats = [
                    ('Fuerza',    char['force'], SABER_BLUE),
                    ('Velocidad', char['speed'],  GREEN),
                    ('Salto',     char['jump'],   ORANGE),
                ]
                for j, (label, val, col) in enumerate(stats):
                    by = 292 + j * 22
                    lbl = self.font_sm.render(label, True, GREY)
                    surf.blit(lbl, (cx - card_w//2 + 8, by))
                    bx = cx - card_w//2 + 75
                    bw = card_w - 85
                    pygame.draw.rect(surf, DARK_GREY, (bx, by+2, bw, 12), border_radius=3)
                    fill = int(bw * val / 10)
                    pygame.draw.rect(surf, col, (bx, by+2, fill, 12), border_radius=3)
                    pygame.draw.rect(surf, lighter(col,40), (bx, by+2, fill, 6), border_radius=3)

                # Descripción
                for k, line in enumerate(char['desc'].split('\n')):
                    dl = self.font_sm.render(line, True, WHITE)
                    surf.blit(dl, dl.get_rect(center=(cx, 360 + k*16)))

            # Sable de luz indicador
            saber_colors_map = {'Azul': SABER_BLUE, 'Verde': SABER_GREEN,
                                'Rojo': SABER_RED, 'Púrpura': SABER_PURPLE}
            sc = saber_colors_map.get(char.get('saber','Azul'), SABER_BLUE)
            pygame.draw.line(surf, sc, (cx-20, 400), (cx+20, 400), 3)
            pygame.draw.line(surf, lighter(sc,80), (cx-20, 400), (cx+20, 400), 1)

            # Flechas de selección
            if selected:
                arrow_y = char_y + 40
                if i > 0:
                    pygame.draw.polygon(surf, YELLOW,
                                       [(card_rect.left-18, arrow_y),
                                        (card_rect.left-4, arrow_y-12),
                                        (card_rect.left-4, arrow_y+12)])
                if i < n-1:
                    pygame.draw.polygon(surf, YELLOW,
                                       [(card_rect.right+18, arrow_y),
                                        (card_rect.right+4, arrow_y-12),
                                        (card_rect.right+4, arrow_y+12)])

        # Instrucciones
        hint1 = self.font_sm.render("← → para elegir    ENTER para confirmar", True, YELLOW)
        surf.blit(hint1, hint1.get_rect(center=(W//2, 435)))

        ctrl = self.font_sm.render(
            "Z: Sable de luz    X: Habilidad de la Fuerza    ESPACIO: Saltar", True, GREY)
        surf.blit(ctrl, ctrl.get_rect(center=(W//2, 455)))


# ──────────────────────────────────────────────────────
#  CINEMÁTICA
# ──────────────────────────────────────────────────────
class CutsceneScene:
    SCENES = [
        ([OBI_WAN, DARTH_VADER],
         ["En una galaxia muy lejana...",
          "Un nuevo mal ha despertado.",
          "La Muerte Negra amenaza toda forma de vida."]),
        ([OBI_WAN, DARTH_VADER],
         ["Por primera vez, los enemigos deben unirse.",
          "Obi-Wan Kenobi y Darth Vader...",
          "aliados por la desesperación."]),
        ([OBI_WAN, DARTH_VADER],
         ["La única esperanza: construir droides gigantes",
          "con las piezas Lego que recuperen en batalla.",
          "¡La guerra de los droides ha comenzado!"]),
    ]

    def __init__(self, scene_index=0, player_char=OBI_WAN):
        self.scene_index = scene_index
        self.player_char = player_char
        # Reemplazar OBI_WAN por el personaje elegido en la primera escena
        chars, lines = self.SCENES[scene_index % len(self.SCENES)]
        self.char_scene = [player_char if c == OBI_WAN else c for c in chars]
        self.lines = lines
        self.font_body = pygame.font.SysFont('Arial', 17)
        self.font_hint = pygame.font.SysFont('Arial', 14)
        self.frame = 0
        self.line_index = 0
        self.displayed = ""
        self.full_text = self.lines[0]
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(100)]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if len(self.displayed) < len(self.full_text):
                self.displayed = self.full_text
            else:
                self.line_index += 1
                if self.line_index >= len(self.lines):
                    return 'level1'
                self.full_text = self.lines[self.line_index]
                self.displayed = ""
        return None

    def update(self):
        self.frame += 1
        if self.frame % 2 == 0 and len(self.displayed) < len(self.full_text):
            self.displayed += self.full_text[len(self.displayed)]

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        for i, ct in enumerate(self.char_scene):
            cx = W // (len(self.char_scene) + 1) * (i + 1)
            draw_minifigure(surf, cx, 390, ct, 1 if i%2==0 else -1, 'idle', self.frame)

        box = pygame.Rect(60, 420, W-120, 110)
        pygame.draw.rect(surf, (10, 20, 50), box, border_radius=8)
        pygame.draw.rect(surf, YELLOW, box, 3, border_radius=8)

        for i, line in enumerate(self.lines[:self.line_index]):
            t = self.font_body.render(line, True, GREY)
            surf.blit(t, (box.x+14, box.y+8+i*22))

        cur = self.font_body.render(self.displayed, True, WHITE)
        surf.blit(cur, (box.x+14, box.y+8+self.line_index*22))

        if (self.frame//15)%2==0 and len(self.displayed)==len(self.full_text):
            pygame.draw.rect(surf, WHITE,
                             (box.x+14+cur.get_width()+2,
                              box.y+10+self.line_index*22, 8, 14))

        if (self.frame//30)%2==0:
            h = self.font_hint.render("ENTER / ESPACIO para continuar", True, GOLD)
            surf.blit(h, h.get_rect(center=(W//2, box.bottom+18)))


# ──────────────────────────────────────────────────────
#  NIVEL 1 - CORREDOR DEATH STAR
# ──────────────────────────────────────────────────────
class Level1Scene:
    LEVEL_W = 3200

    def __init__(self, player_char=OBI_WAN):
        self.player_char = player_char
        self.font     = pygame.font.SysFont('Arial Black', 18)
        self.font_sm  = pygame.font.SysFont('Arial', 14)
        self.frame    = 0
        self.cam_x    = 0.0
        self.stars    = [(random.randint(0, self.LEVEL_W), random.randint(0, H))
                         for _ in range(200)]
        self._build_level()
        self.next_scene    = None
        self.transition_timer = 0
        self.build_anim    = 0
        self.build_phase   = None
        self.message       = ""
        self.message_timer = 0
        self.death_timer   = 0
        self.enemy_shots   = []   # lista de disparos de Stormtroopers activos

    def _build_level(self):
        plat_data = [
            (0,    568, 3200, 32, DARK_GREY),
            (150,  460,  200, 22, GREY),
            (390,  390,  170, 22, GREY),
            (600,  460,  160, 22, DARK_GREY),
            (810,  340,  210, 22, GREY),
            (1060, 430,  180, 22, GREY),
            (1280, 360,  210, 22, DARK_GREY),
            (1510, 278,  190, 22, GREY),
            (1730, 390,  170, 22, GREY),
            (1940, 318,  210, 22, DARK_GREY),
            (2160, 438,  190, 22, GREY),
            (2380, 358,  160, 22, GREY),
            (2560, 278,  210, 22, DARK_GREY),
            (2790, 398,  190, 22, GREY),
            (2980, 298,  220, 270, DARK_GREY),
            (0,    0,     20, 600, BLACK),
        ]
        self.platforms = [Platform(x, y, w, h, c) for x, y, w, h, c in plat_data]

        self.player = Player(60, 490, self.player_char)

        enemy_data = [
            (260, 415, 80), (495, 345, 70), (710, 415, 90),
            (930, 295, 80), (1210, 315, 100),(1410, 415, 80),
            (1660, 233, 80), (1860, 345, 90), (2090, 273, 80),
            (2310, 393, 90), (2510, 233, 80),
        ]
        self.enemies = [Stormtrooper(x, y, pd) for x, y, pd in enemy_data]
        self.flying_studs = []

        colors_cycle = [RED, BLUE, GREEN, ORANGE, YELLOW, TAN, RED, BLUE]
        piece_positions = [
            (185,430),(225,430),(415,360),(450,360),
            (625,430),(665,430),(840,310),(890,310),
            (1080,400),(1130,400),(1310,330),(1355,330),
            (1530,248),(1580,248),(1750,360),(1795,360),
            (1960,288),(2010,288),(2180,408),(2225,408),
            (2410,328),(2455,328),(2580,248),
        ]
        self.pieces = [LegoPiece(x, y, colors_cycle[i%len(colors_cycle)])
                       for i, (x, y) in enumerate(piece_positions)]

        self.gold_bricks = [
            GoldBrick(755, 292),
            GoldBrick(1610, 230),
            GoldBrick(2310, 308),
        ]

    def handle_event(self, event):
        return None

    def update(self):
        self.frame += 1
        keys = pygame.key.get_pressed()

        if self.build_phase is None and not self.player.dead:
            self.player.handle_input(keys)

        self.player.update(self.platforms)

        # ── Ataque sable: coords en mundo (player.rect ya está en mundo) ──
        attack_rect, attack_id = self.player.get_attack_rect()
        # Rect de la Fuerza también en coords de mundo
        force_rect = self.player.get_force_rect()

        for e in self.enemies:
            e.update(self.platforms, attack_rect, attack_id, force_rect,
                     player_cx=self.player.rect.centerx)
            # Recoger studs soltados
            for s in e.stud_drop:
                if s not in self.flying_studs:
                    self.flying_studs.append(s)
            e.stud_drop.clear()
            # Recoger disparos nuevos
            for shot in e.pending_shots:
                self.enemy_shots.append(shot)
            e.pending_shots.clear()

        # ── Mover disparos de Stormtroopers ──
        SHOT_RANGE = 160   # píxeles máximos que viaja el láser
        for shot in self.enemy_shots:
            shot['x'] += shot['vx']
        # Colisión disparo → jugador
        if not self.player.dead:
            for shot in self.enemy_shots[:]:
                sr = pygame.Rect(int(shot['x'])-5, int(shot['y'])-5, 10, 10)
                if sr.colliderect(self.player.rect):
                    self.player._take_damage()
                    self.enemy_shots.remove(shot)
        # Eliminar disparos que superaron el alcance máximo o salieron del nivel
        self.enemy_shots = [s for s in self.enemy_shots
                            if abs(s['x'] - s['origin_x']) < SHOT_RANGE
                            and 0 <= s['x'] <= self.LEVEL_W]

        for s in self.flying_studs:
            s.update(self.player)
        self.flying_studs = [s for s in self.flying_studs
                             if not s.collected or s.life > 0]

        for p in self.pieces:
            p.update()
            if p.check_collect(self.player):
                self.player.collect_piece(p)
                self._show_message(f"+1 Pieza  ({self.player.pieces}/{PIECES_TO_BUILD})")

        for g in self.gold_bricks:
            g.update()
            if g.check_collect(self.player):
                self.player.collect_gold()
                self._show_message("¡LADRILLO DORADO!  +500 studs")

        # Cámara suave
        target = self.player.rect.centerx - W // 3
        target = max(0, min(target, self.LEVEL_W - W))
        self.cam_x += (target - self.cam_x) * 0.12

        if self.message_timer > 0:
            self.message_timer -= 1

        # ¿Llegó al final con piezas suficientes?
        if (self.player.pieces >= PIECES_TO_BUILD
                and self.build_phase is None
                and self.player.rect.x > 2920):
            self.build_phase = 'building'
            self._show_message("¡Piezas suficientes!  Ensamblando droide...")

        if self.build_phase == 'building':
            self.build_anim += 1
            if self.build_anim > 120:
                self.build_phase = 'done'
                self.next_scene  = 'droid_battle'
                self.transition_timer = 60

        if self.next_scene and self.transition_timer > 0:
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                return self.next_scene

        # Muerte del jugador → animación Lego y respawn (no reinicia el nivel)
        if self.player.dead:
            if self.player.death_timer > 80:
                # Respawn estilo Lego: reaparece en la misma posición con HP lleno
                self.player.dead = False
                self.player.death_timer = 0
                self.player.hp = self.player.max_hp
                self.player.rect.x = self.player.last_safe_x
                self.player.rect.y = 300
                self.player.vy = 0
                self.player.inv_timer = 120
                # Penalización de studs
                penalty = min(self.player.studs, 200)
                self.player.studs -= penalty
                self._show_message(f"¡Resucitado! -{penalty} studs")

        return None

    def _show_message(self, text):
        self.message = text
        self.message_timer = 130

    def draw(self, surf):
        draw_background(surf, int(self.cam_x), self.stars)

        for p in self.platforms:
            p.draw(surf, int(self.cam_x))

        for p in self.pieces:
            p.draw(surf, int(self.cam_x))

        for g in self.gold_bricks:
            g.draw(surf, int(self.cam_x))

        for e in self.enemies:
            e.draw(surf, int(self.cam_x))

        for s in self.flying_studs:
            s.draw(surf, int(self.cam_x))

        # Disparos de Stormtroopers (rayos rojos)
        for shot in self.enemy_shots:
            sx2 = int(shot['x'] - self.cam_x)
            sy2 = int(shot['y'])
            pygame.draw.circle(surf, RED,   (sx2, sy2), 5)
            pygame.draw.circle(surf, (255,140,140), (sx2, sy2), 3)
            pygame.draw.circle(surf, WHITE, (sx2, sy2), 1)
            # Cola del disparo
            tail_x = sx2 - int(shot['vx'] * 4)
            pygame.draw.line(surf, (200, 50, 50), (sx2, sy2), (tail_x, sy2), 3)

        self.player.draw(surf, int(self.cam_x))

        if self.build_phase in ('building', 'done'):
            self._draw_build_anim(surf)

        draw_hud(surf, self.player.pieces, PIECES_TO_BUILD,
                 self.player.gold_bricks, self.player.studs,
                 self.player.hp, self.player.max_hp)

        # Leyenda de controles (primera vez visible)
        if self.frame < 300:
            ctrl = self.font_sm.render(
                "Z: Sable   X: Fuerza   ESPACIO: Saltar", True, WHITE)
            surf.blit(ctrl, ctrl.get_rect(center=(W//2, 575)))

        # Mensaje flotante
        if self.message_timer > 0:
            alpha = min(255, self.message_timer * 3)
            msg_surf = self.font.render(self.message, True, GOLD)
            msg_surf.set_alpha(alpha)
            surf.blit(msg_surf, msg_surf.get_rect(center=(W//2, 110)))

        # Objetivo
        if self.player.pieces < PIECES_TO_BUILD and self.frame >= 300:
            obj = self.font_sm.render(
                f"Recogé piezas y avanzá → ({self.player.pieces}/{PIECES_TO_BUILD})",
                True, WHITE)
            surf.blit(obj, obj.get_rect(center=(W//2, 580)))

        # Fade
        if self.transition_timer > 0 and self.next_scene:
            fade = pygame.Surface((W, H))
            fade.fill(BLACK)
            fade.set_alpha(int(255 * (1 - self.transition_timer / 60)))
            surf.blit(fade, (0, 0))

    def _draw_build_anim(self, surf):
        t = self.build_anim
        cx_b, cy_b = W - 180, 460
        for i in range(min(t//4, 24)):
            angle = i*15 + t*2
            dist  = max(0, 80 - t*0.5)
            px = cx_b + int(math.cos(math.radians(angle)) * dist)
            py = cy_b + int(math.sin(math.radians(angle)) * dist) - 30
            c = [RED,BLUE,GREEN,ORANGE,YELLOW,TAN][i%6]
            pygame.draw.rect(surf, c, (px-4, py-4, 8, 8), border_radius=2)

        if t > 60:
            progress = min(1.0, (t-60)/60)
            droid_y  = int(600 - progress * 200)
            draw_droid(surf, cx_b, droid_y, 'alliance', 1.0, t)
            if t > 100:
                msg = self.font.render("¡DROIDE LISTO!", True, YELLOW)
                surf.blit(msg, msg.get_rect(center=(cx_b, 268)))


# ──────────────────────────────────────────────────────
#  BATALLA DE DROIDES
# ──────────────────────────────────────────────────────
class DrBattleScene:
    def __init__(self, player_char=OBI_WAN):
        self.player_char = player_char
        self.font_big = pygame.font.SysFont('Impact', 44)
        self.font     = pygame.font.SysFont('Arial Black', 20)
        self.font_sm  = pygame.font.SysFont('Arial', 15)
        self.frame    = 0
        self.player_hp = 100
        self.enemy_hp  = 100
        self.player_atk_cd = 0
        self.enemy_atk_cd  = random.randint(80, 130)
        self.last_player_hit = 0
        self.last_enemy_hit  = 0
        self.battle_over  = False
        self.winner       = None
        self.ending_timer = 0
        self.projectiles  = []  # [x, y, vx, is_player]
        self.shake = 0
        self.stars = [(random.randint(0,W), random.randint(0,H)) for _ in range(100)]

    def handle_event(self, event):
        return None

    def update(self):
        self.frame += 1
        if self.shake > 0:
            self.shake -= 1

        if self.battle_over:
            self.ending_timer += 1
            if self.ending_timer > 190:
                return 'victory' if self.winner == 'player' else 'droid_battle'
            return None

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_z] or keys[pygame.K_j] or keys[pygame.K_RETURN]) and self.player_atk_cd <= 0:
            self.player_atk_cd = 35
            self.projectiles.append([165, 415, 6, True])

        if self.player_atk_cd > 0:
            self.player_atk_cd -= 1

        self.enemy_atk_cd -= 1
        if self.enemy_atk_cd <= 0:
            self.enemy_atk_cd = random.randint(65, 120)
            self.projectiles.append([W-165, 415, -6, False])

        for p in self.projectiles:
            p[0] += p[2]

        for p in self.projectiles[:]:
            if p[3] and p[0] > W-200:
                self.enemy_hp   -= 12
                self.last_enemy_hit = 20
                self.shake = 8
                self.projectiles.remove(p)
            elif not p[3] and p[0] < 200:
                self.player_hp  -= 9
                self.last_player_hit = 20
                self.shake = 8
                self.projectiles.remove(p)

        self.projectiles = [p for p in self.projectiles if 0 <= p[0] <= W]

        if self.last_player_hit > 0: self.last_player_hit -= 1
        if self.last_enemy_hit  > 0: self.last_enemy_hit  -= 1

        if self.player_hp <= 0 and not self.battle_over:
            self.player_hp  = 0
            self.battle_over = True
            self.winner = 'enemy'
        if self.enemy_hp  <= 0 and not self.battle_over:
            self.enemy_hp   = 0
            self.battle_over = True
            self.winner = 'player'

        return None

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)
        draw_lego_brick(surf, 0, 490, W, 110, DARK_GREY)

        ox = random.randint(-self.shake, self.shake) if self.shake else 0
        oy = random.randint(-self.shake, self.shake) if self.shake else 0

        draw_droid(surf, 185+ox, 490+oy, 'alliance', self.player_hp/100, self.frame)
        draw_droid(surf, W-185+ox, 490+oy, 'muerte',  self.enemy_hp/100,  self.frame)

        vs = self.font_big.render("VS", True, YELLOW)
        surf.blit(vs, vs.get_rect(center=(W//2, 340)))

        for p in self.projectiles:
            color = SABER_BLUE if p[3] else SABER_PURPLE
            pygame.draw.circle(surf, color, (int(p[0]), int(p[1])), 7)
            pygame.draw.circle(surf, WHITE,  (int(p[0]), int(p[1])), 3)
            tail = int(p[0] - p[2]*7)
            pygame.draw.line(surf, lighter(color,50), (int(p[0]),int(p[1])), (tail,int(p[1])), 4)

        self._draw_hp_bar(surf, 28, 38, self.player_hp, 100, BLUE,   "TU DROIDE")
        self._draw_hp_bar(surf, W//2+20, 38, self.enemy_hp,  100, PURPLE, "DROIDE MUERTE")

        if not self.battle_over:
            hint = self.font_sm.render("Z / J / ENTER → ¡ATACAR!", True, YELLOW)
            surf.blit(hint, hint.get_rect(center=(W//2, 548)))
            if self.player_atk_cd > 0:
                cd = self.font_sm.render(f"Recargando... {self.player_atk_cd//10+1}s", True, GREY)
                surf.blit(cd, cd.get_rect(center=(W//2, 566)))

        if self.battle_over:
            ov = pygame.Surface((W, 100), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            surf.blit(ov, (0, H//2-50))
            if self.winner == 'player':
                txt = self.font_big.render("¡VICTORIA!", True, GOLD)
                sub = self.font.render("¡La Muerte Negra ha sido derrotada!", True, WHITE)
            else:
                txt = self.font_big.render("DERROTA...", True, RED)
                sub = self.font.render("Reintentando...", True, GREY)
            surf.blit(txt, txt.get_rect(center=(W//2, H//2-20)))
            surf.blit(sub, sub.get_rect(center=(W//2, H//2+25)))

    def _draw_hp_bar(self, surf, x, y, hp, max_hp, color, label):
        bw = W//2 - 52
        bh = 24
        lbl = pygame.font.SysFont('Arial Black', 13).render(label, True, WHITE)
        surf.blit(lbl, (x, y-16))
        pygame.draw.rect(surf, DARK_GREY, (x, y, bw, bh), border_radius=4)
        fill = int(bw * max(0, hp) / max_hp)
        if fill > 0:
            pygame.draw.rect(surf, color, (x, y, fill, bh), border_radius=4)
            pygame.draw.rect(surf, lighter(color, 40), (x, y, fill, bh//2), border_radius=4)
        pygame.draw.rect(surf, WHITE, (x, y, bw, bh), 2, border_radius=4)
        hp_t = pygame.font.SysFont('Arial Black', 13).render(f"{max(0,hp)}%", True, WHITE)
        surf.blit(hp_t, (x+bw//2-hp_t.get_width()//2, y+4))


# ──────────────────────────────────────────────────────
#  VICTORIA
# ──────────────────────────────────────────────────────
class VictoryScene:
    def __init__(self, player_char=OBI_WAN):
        self.player_char = player_char
        self.font_big = pygame.font.SysFont('Impact', 58)
        self.font     = pygame.font.SysFont('Arial Black', 20)
        self.font_sm  = pygame.font.SysFont('Arial', 16)
        self.frame = 0
        self.stars = [(random.randint(0,W), random.randint(0,H)) for _ in range(120)]
        self.confetti = [
            (random.randint(0,W), random.randint(-H,0),
             random.choice([RED,BLUE,GREEN,ORANGE,YELLOW,PURPLE]),
             random.uniform(-1,1), random.uniform(1,4))
            for _ in range(80)
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return 'title'
        return None

    def update(self):
        self.frame += 1
        new = []
        for x, y, c, vx, vy in self.confetti:
            ny = y + vy
            nx = x + vx
            if ny > H+20:
                ny = -20
                nx = random.randint(0, W)
            new.append((nx, ny, c, vx, vy))
        self.confetti = new

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        for x, y, c, _, _ in self.confetti:
            pygame.draw.rect(surf, c, (int(x)-3, int(y)-3, 6, 6), border_radius=1)

        chars = [(self.player_char, 1), (DARTH_VADER, -1), (YODA, 1)]
        for i, (ct, d) in enumerate(chars):
            cx = 200 + i*280
            bob = int(math.sin(self.frame*0.1+i)*5)
            draw_minifigure(surf, cx, 420+bob, ct, d, 'idle', self.frame)

        _draw_lego_text(surf, pygame.font.SysFont('Impact',56),
                        "¡NIVEL COMPLETADO!", W//2, 148, GOLD, BLACK)

        lines = [
            "¡La Muerte Negra ha sido detenida... por ahora!",
            "",
            "Darth Vader: 'Impresionante, aliado.'",
            "La alianza imposible sigue adelante.",
            "",
            "→ Próximo nivel: El contraataque de la Muerte Negra",
        ]
        font = pygame.font.SysFont('Arial', 18)
        for i, line in enumerate(lines):
            t = font.render(line, True, WHITE)
            surf.blit(t, t.get_rect(center=(W//2, 268+i*28)))

        if (self.frame//30)%2==0:
            hint = self.font_sm.render("ENTER / ESPACIO → Menú principal", True, YELLOW)
            surf.blit(hint, hint.get_rect(center=(W//2, 575)))


# ──────────────────────────────────────────────────────
#  Utilidad: texto con borde negro
# ──────────────────────────────────────────────────────
def _draw_lego_text(surf, font, text, cx, cy, color, shadow_color):
    for dx, dy in [(-3,3),(3,3),(-3,-3),(3,-3),(0,4)]:
        s = font.render(text, True, shadow_color)
        surf.blit(s, s.get_rect(center=(cx+dx, cy+dy)))
    t = font.render(text, True, color)
    surf.blit(t, t.get_rect(center=(cx, cy)))
