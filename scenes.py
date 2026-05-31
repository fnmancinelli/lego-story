# LEGO Story - Escenas del juego
import pygame
import random
import math
from settings import *
from draw_utils import (draw_background, draw_lego_brick, draw_hud,
                        draw_minifigure, draw_droid, draw_lego_piece,
                        draw_gold_brick, lighter, darker)
from entities import Platform, Player, Stormtrooper, LegoPiece, GoldBrick, FlyingStud


# ─────────────────────────────────────────────
#  PANTALLA DE TÍTULO
# ─────────────────────────────────────────────
class TitleScene:
    def __init__(self):
        self.font_title = pygame.font.SysFont('Impact', 72)
        self.font_sub   = pygame.font.SysFont('Arial Black', 22)
        self.font_hint  = pygame.font.SysFont('Arial', 16)
        self.frame = 0
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(120)]
        # Minifiguras decorativas en el título
        self.chars = [
            (200, 480, OBI_WAN, 1),
            (800, 480, DARTH_VADER, -1),
            (500, 490, MUERTE_NEGRA, 1),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return 'intro'
        return None

    def update(self):
        self.frame += 1

    def draw(self, surf):
        surf.fill(SPACE_BG)
        # Estrellas
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        # Suelo estilo Lego
        draw_lego_brick(surf, 0, 510, W, 90, DARK_GREY)

        # Personajes animados
        for cx, cy, ct, d in self.chars:
            state = 'walk' if ct != MUERTE_NEGRA else 'idle'
            draw_minifigure(surf, cx, cy, ct, d, state, self.frame)

        # Sable de Obi-Wan y Vader chocando (decorativo)
        glow = int(abs(math.sin(self.frame * 0.05)) * 40)
        impact_x, impact_y = W//2, 440
        pygame.draw.line(surf, (80+glow, 80+glow, 255),
                         (200+18, 466), (impact_x, impact_y), 4)
        pygame.draw.line(surf, (255, 40+glow, 40+glow),
                         (800-18, 466), (impact_x, impact_y), 4)
        pygame.draw.circle(surf, WHITE, (impact_x, impact_y), 4+glow//20)

        # Título amarillo estilo Lego
        pulse = int(abs(math.sin(self.frame * 0.03)) * 8)
        _draw_lego_text(surf, self.font_title, "LEGO", W//2, 120, GOLD, BLACK)
        _draw_lego_text(surf, self.font_title, "STORY", W//2, 200, RED, BLACK)

        sub = self.font_sub.render("La Alianza Imposible", True, WHITE)
        surf.blit(sub, sub.get_rect(center=(W//2, 295)))

        # Prompt parpadeante
        if (self.frame // 30) % 2 == 0:
            hint = self.font_hint.render("Presioná ENTER o ESPACIO para comenzar", True, YELLOW)
            surf.blit(hint, hint.get_rect(center=(W//2, 560)))

        # Controles mini
        ctrl = self.font_hint.render(
            "Flechas/WASD: mover   ESPACIO: saltar   Z/J: atacar", True, GREY)
        surf.blit(ctrl, ctrl.get_rect(center=(W//2, 580)))


# ─────────────────────────────────────────────
#  CINEMÁTICA / HISTORIA
# ─────────────────────────────────────────────
class CutsceneScene:
    SCENES = [
        # (personajes, texto)
        ([OBI_WAN, DARTH_VADER],
         ["En una galaxia muy lejana...",
          "Un nuevo mal ha despertado.",
          "La Muerte Negra amenaza toda forma de vida."]),
        ([OBI_WAN, DARTH_VADER],
         ["Por primera vez, los enemigos deben unirse.",
          "Obi-Wan Kenobi y Darth Vader...",
          "aliados por la desesperación."]),
        ([OBI_WAN, DARTH_VADER],
         ["La única esperanza:",
          "construir droides gigantes de Lego",
          "para combatir los ejércitos de La Muerte Negra."]),
        ([OBI_WAN],
         ["Recoge piezas de Lego en cada nivel.",
          "Con suficientes piezas, tu droide se ensamblará.",
          "¡La batalla final te espera!"]),
    ]

    def __init__(self, scene_index=0):
        self.scene_index = scene_index
        self.char_scene, self.lines = self.SCENES[scene_index % len(self.SCENES)]
        self.font_big  = pygame.font.SysFont('Arial Black', 20)
        self.font_body = pygame.font.SysFont('Arial', 17)
        self.font_hint = pygame.font.SysFont('Arial', 14)
        self.frame = 0
        self.line_index = 0
        self.char_timer = 0
        self.displayed = ""
        self.full_text = self.lines[self.line_index]
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(100)]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Avanzar texto o saltar a nivel
            if len(self.displayed) < len(self.full_text):
                self.displayed = self.full_text
                self.char_timer = 9999
            else:
                self.line_index += 1
                if self.line_index >= len(self.lines):
                    return 'level1'
                self.full_text = self.lines[self.line_index]
                self.displayed = ""
                self.char_timer = 0
        return None

    def update(self):
        self.frame += 1
        self.char_timer += 1
        if self.char_timer % 2 == 0 and len(self.displayed) < len(self.full_text):
            self.displayed += self.full_text[len(self.displayed)]

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        # Personajes
        for i, ct in enumerate(self.char_scene):
            cx = W // (len(self.char_scene) + 1) * (i + 1)
            draw_minifigure(surf, cx, 380, ct, 1 if i % 2 == 0 else -1, 'idle', self.frame)

        # Caja de texto
        box = pygame.Rect(60, 420, W - 120, 110)
        pygame.draw.rect(surf, (10, 20, 50), box, border_radius=8)
        pygame.draw.rect(surf, YELLOW, box, 3, border_radius=8)

        # Líneas anteriores (gris)
        for i, line in enumerate(self.lines[:self.line_index]):
            t = self.font_body.render(line, True, GREY)
            surf.blit(t, (box.x + 14, box.y + 8 + i * 22))

        # Línea actual (blanco, efecto máquina de escribir)
        cur = self.font_body.render(self.displayed, True, WHITE)
        surf.blit(cur, (box.x + 14, box.y + 8 + self.line_index * 22))

        # Cursor parpadeante
        if (self.frame // 15) % 2 == 0 and len(self.displayed) == len(self.full_text):
            pygame.draw.rect(surf, WHITE,
                             (box.x + 14 + cur.get_width() + 2,
                              box.y + 10 + self.line_index * 22, 8, 14))

        # Hint
        if (self.frame // 30) % 2 == 0:
            h = self.font_hint.render("ENTER / ESPACIO para continuar", True, GOLD)
            surf.blit(h, h.get_rect(center=(W//2, box.bottom + 18)))

        # Número de escena
        sc = self.font_hint.render(
            f"Escena {self.line_index+1}/{len(self.lines)}", True, DARK_GREY)
        surf.blit(sc, (box.x + 4, box.y - 18))


# ─────────────────────────────────────────────
#  NIVEL 1 - CORREDOR DEATH STAR
# ─────────────────────────────────────────────
class Level1Scene:
    LEVEL_W = 3200

    def __init__(self):
        self.font = pygame.font.SysFont('Arial Black', 18)
        self.font_sm = pygame.font.SysFont('Arial', 14)
        self.frame = 0
        self.cam_x = 0.0
        self.stars = [(random.randint(0, self.LEVEL_W), random.randint(0, H))
                      for _ in range(200)]
        self._build_level()
        self.next_scene = None
        self.transition_timer = 0
        self.build_anim = 0   # animación construcción droide
        self.build_phase = None  # None / 'building' / 'done'
        self.message = ""
        self.message_timer = 0

    def _build_level(self):
        # Plataformas (x, y, w, h, color)
        plat_data = [
            (0,    570, 3200,  30, DARK_GREY),   # suelo completo
            (150,  460,  180,  20, GREY),
            (380,  390,  160,  20, GREY),
            (590,  460,  150,  20, DARK_GREY),
            (800,  340,  200,  20, GREY),
            (1050, 430,  170,  20, GREY),
            (1270, 360,  200,  20, DARK_GREY),
            (1500, 280,  180,  20, GREY),
            (1720, 390,  160,  20, GREY),
            (1930, 320,  200,  20, DARK_GREY),
            (2150, 440,  180,  20, GREY),
            (2370, 360,  150,  20, GREY),
            (2550, 280,  200,  20, DARK_GREY),
            (2780, 400,  180,  20, GREY),
            (2970, 300,  230, 270, DARK_GREY),   # pared final (zona droide)
            # Muros laterales
            (0,    0,    20, 600, BLACK),
        ]
        self.platforms = [Platform(x, y, w, h, c) for x, y, w, h, c in plat_data]

        # Jugador
        self.player = Player(60, 520, OBI_WAN)

        # Enemigos Stormtrooper
        enemy_data = [
            (250, 416, 80), (480, 346, 70), (700, 416, 90),
            (920, 296, 80), (1200, 316, 100), (1400, 416, 80),
            (1650, 236, 80), (1850, 346, 90), (2080, 276, 80),
            (2300, 396, 90), (2500, 236, 80),
        ]
        self.enemies = [Stormtrooper(x, y, pd) for x, y, pd in enemy_data]

        # Studs volantes (de enemigos muertos)
        self.flying_studs = []

        # Piezas de Lego coleccionables
        piece_positions = [
            (180, 430), (220, 430), (410, 360), (440, 360),
            (620, 430), (660, 430), (830, 310), (880, 310),
            (1070, 400), (1120, 400), (1300, 330), (1340, 330),
            (1520, 250), (1570, 250), (1740, 360), (1780, 360),
            (1950, 290), (2000, 290), (2170, 410), (2210, 410),
            (2400, 330), (2450, 330), (2570, 250),
        ]
        colors = [RED, BLUE, GREEN, ORANGE, YELLOW, TAN, RED, BLUE]
        self.pieces = [LegoPiece(x, y, colors[i % len(colors)])
                       for i, (x, y) in enumerate(piece_positions)]

        # Ladrillos dorados
        self.gold_bricks = [
            GoldBrick(750, 290),
            GoldBrick(1600, 230),
            GoldBrick(2300, 310),
        ]

    def handle_event(self, event):
        return None  # input manejado con get_pressed

    def update(self):
        self.frame += 1
        keys = pygame.key.get_pressed()

        if self.build_phase is None:
            self.player.handle_input(keys)

        # Update player
        self.player.update(self.platforms)

        # Update enemies
        attack_rect = self.player.get_attack_rect()
        # Mover attack_rect a coords de mundo
        world_attack = None
        if attack_rect:
            world_attack = pygame.Rect(
                attack_rect.x + int(self.cam_x), attack_rect.y,
                attack_rect.w, attack_rect.h)

        for e in self.enemies:
            e.update(self.platforms, world_attack)
            for s in e.stud_drop:
                if s not in self.flying_studs:
                    self.flying_studs.append(s)
            e.stud_drop.clear()

        # Studs volantes
        for s in self.flying_studs:
            s.update(self.player)
        self.flying_studs = [s for s in self.flying_studs if not s.collected or s.life > 0]

        # Piezas
        for p in self.pieces:
            p.update()
            if p.check_collect(self.player):
                self.player.collect_piece(p)
                self._show_message(f"+1 Pieza ({self.player.pieces}/{PIECES_TO_BUILD})")

        # Ladrillos dorados
        for g in self.gold_bricks:
            g.update()
            if g.check_collect(self.player):
                self.player.collect_gold()
                self._show_message("¡LADRILLO DORADO! +500 studs")

        # Cámara suave
        target_cam = self.player.rect.centerx - W // 3
        target_cam = max(0, min(target_cam, self.LEVEL_W - W))
        self.cam_x += (target_cam - self.cam_x) * 0.12

        # Mensaje
        if self.message_timer > 0:
            self.message_timer -= 1

        # ¿Suficientes piezas para construir el droide?
        if (self.player.pieces >= PIECES_TO_BUILD
                and self.build_phase is None
                and self.player.rect.x > 2900):
            self.build_phase = 'building'
            self._show_message("¡PIEZAS SUFICIENTES! Construyendo droide...")

        # Animación construcción
        if self.build_phase == 'building':
            self.build_anim += 1
            if self.build_anim > 120:
                self.build_phase = 'done'
                self.next_scene = 'droid_battle'
                self.transition_timer = 60

        # Transición
        if self.next_scene and self.transition_timer > 0:
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                return self.next_scene

        # Muerte del jugador
        if self.player.dead:
            self.transition_timer += 1
            if self.transition_timer > 90:
                return 'level1'  # reiniciar nivel

        return None

    def _show_message(self, text):
        self.message = text
        self.message_timer = 120

    def draw(self, surf):
        draw_background(surf, int(self.cam_x), self.stars)

        # Plataformas
        for p in self.platforms:
            p.draw(surf, int(self.cam_x))

        # Piezas coleccionables
        for p in self.pieces:
            p.draw(surf, int(self.cam_x))

        # Ladrillos dorados
        for g in self.gold_bricks:
            g.draw(surf, int(self.cam_x))

        # Enemigos
        for e in self.enemies:
            e.draw(surf, int(self.cam_x))

        # Studs volantes
        for s in self.flying_studs:
            s.draw(surf, int(self.cam_x))

        # Jugador
        self.player.draw(surf, int(self.cam_x))

        # Animación construcción droide
        if self.build_phase in ('building', 'done'):
            self._draw_build_anim(surf)

        # HUD
        draw_hud(surf, self.player.pieces, PIECES_TO_BUILD,
                 self.player.gold_bricks, self.player.studs,
                 self.player.hp, self.player.max_hp)

        # Mensaje flotante
        if self.message_timer > 0:
            alpha = min(255, self.message_timer * 3)
            msg_surf = self.font.render(self.message, True, GOLD)
            msg_surf.set_alpha(alpha)
            surf.blit(msg_surf, msg_surf.get_rect(center=(W//2, 110)))

        # Indicador de objetivo
        if self.player.pieces < PIECES_TO_BUILD:
            obj = self.font_sm.render(
                "Recoge piezas → llega al final del nivel", True, WHITE)
            surf.blit(obj, obj.get_rect(center=(W//2, 580)))
        elif self.build_phase is None:
            obj = self.font_sm.render(
                "¡Avanza hasta el final del nivel!", True, GREEN)
            surf.blit(obj, obj.get_rect(center=(W//2, 580)))

        # Fade in/out
        if self.transition_timer > 0 and self.next_scene:
            fade = pygame.Surface((W, H))
            fade.fill(BLACK)
            alpha = int(255 * (1 - self.transition_timer / 60))
            fade.set_alpha(alpha)
            surf.blit(fade, (0, 0))

    def _draw_build_anim(self, surf):
        t = self.build_anim
        # Piezas volando hacia el centro
        cx, cy = W - 160, 450
        for i in range(min(t // 4, 24)):
            angle = i * 15 + t * 2
            dist = max(0, 80 - t * 0.5)
            px = cx + int(math.cos(math.radians(angle)) * dist)
            py = cy + int(math.sin(math.radians(angle)) * dist) - 30
            c = [RED, BLUE, GREEN, ORANGE, YELLOW, TAN][i % 6]
            pygame.draw.rect(surf, c, (px-4, py-4, 8, 8), border_radius=2)

        if t > 60:
            # Droide emergiendo
            progress = min(1.0, (t - 60) / 60)
            droid_y = int(600 - progress * 200)
            draw_droid(surf, cx, droid_y, 'alliance', 1.0, t)
            if t > 100:
                msg = self.font.render("¡DROIDE LISTO!", True, YELLOW)
                surf.blit(msg, msg.get_rect(center=(cx, 260)))


# ─────────────────────────────────────────────
#  BATALLA DE DROIDES (boss)
# ─────────────────────────────────────────────
class DrBattleScene:
    def __init__(self):
        self.font_big  = pygame.font.SysFont('Impact', 42)
        self.font      = pygame.font.SysFont('Arial Black', 20)
        self.font_sm   = pygame.font.SysFont('Arial', 15)
        self.frame = 0
        self.player_hp = 100
        self.enemy_hp  = 100
        self.player_attack_timer = 0
        self.enemy_attack_timer  = random.randint(80, 140)
        self.last_player_hit = 0
        self.last_enemy_hit  = 0
        self.battle_over = False
        self.winner = None
        self.ending_timer = 0
        self.projectiles = []  # (x, y, vx, is_player)
        self.shake = 0
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(100)]

    def handle_event(self, event):
        return None

    def update(self):
        self.frame += 1
        if self.shake > 0:
            self.shake -= 1

        if self.battle_over:
            self.ending_timer += 1
            if self.ending_timer > 180:
                if self.winner == 'player':
                    return 'victory'
                else:
                    return 'droid_battle'  # reintentar
            return None

        keys = pygame.key.get_pressed()

        # Ataque jugador
        if (keys[pygame.K_z] or keys[pygame.K_j] or keys[pygame.K_RETURN]):
            if self.player_attack_timer <= 0:
                self.player_attack_timer = 35
                self.projectiles.append([160, 420, 5, True])

        if self.player_attack_timer > 0:
            self.player_attack_timer -= 1

        # IA enemigo ataca automáticamente
        self.enemy_attack_timer -= 1
        if self.enemy_attack_timer <= 0:
            self.enemy_attack_timer = random.randint(70, 130)
            self.projectiles.append([W - 160, 420, -5, False])

        # Mover proyectiles
        for p in self.projectiles:
            p[0] += p[2]

        # Colisiones proyectiles
        for p in self.projectiles[:]:
            if p[3]:  # del jugador → golpea enemigo
                if p[0] > W - 200:
                    self.enemy_hp -= 12
                    self.last_enemy_hit = 20
                    self.shake = 8
                    self.projectiles.remove(p)
            else:  # del enemigo → golpea jugador
                if p[0] < 200:
                    self.player_hp -= 10
                    self.last_player_hit = 20
                    self.shake = 8
                    self.projectiles.remove(p)

        # Proyectiles fuera de pantalla
        self.projectiles = [p for p in self.projectiles
                            if 0 <= p[0] <= W and p in self.projectiles]

        if self.last_player_hit > 0:
            self.last_player_hit -= 1
        if self.last_enemy_hit > 0:
            self.last_enemy_hit -= 1

        # ¿Fin de batalla?
        if self.player_hp <= 0 and not self.battle_over:
            self.player_hp = 0
            self.battle_over = True
            self.winner = 'enemy'
        if self.enemy_hp <= 0 and not self.battle_over:
            self.enemy_hp = 0
            self.battle_over = True
            self.winner = 'player'

        return None

    def draw(self, surf):
        # Fondo
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)
        draw_lego_brick(surf, 0, 490, W, 110, DARK_GREY)

        # Shake de pantalla
        ox = random.randint(-self.shake, self.shake) if self.shake else 0
        oy = random.randint(-self.shake, self.shake) if self.shake else 0

        # Droide jugador (izquierda)
        d_hp = self.player_hp / 100
        draw_droid(surf, 180 + ox, 490 + oy, 'alliance', d_hp, self.frame)

        # Droide enemigo (derecha)
        e_hp = self.enemy_hp / 100
        draw_droid(surf, W - 180 + ox, 490 + oy, 'muerte', e_hp, self.frame)

        # VS en el centro
        vs = self.font_big.render("VS", True, YELLOW)
        surf.blit(vs, vs.get_rect(center=(W//2, 350)))

        # Proyectiles (disparos de los droides)
        for p in self.projectiles:
            color = SABER_BLUE if p[3] else SABER_PURPLE
            pygame.draw.circle(surf, color, (int(p[0]), int(p[1])), 6)
            pygame.draw.circle(surf, WHITE, (int(p[0]), int(p[1])), 3)
            # Cola del disparo
            tail_x = int(p[0] - p[2] * 6)
            pygame.draw.line(surf, lighter(color, 40), (int(p[0]), int(p[1])), (tail_x, int(p[1])), 3)

        # Barras de vida
        self._draw_hp_bar(surf, 30, 40, self.player_hp, 100, BLUE, "TU DROIDE")
        self._draw_hp_bar(surf, W//2 + 20, 40, self.enemy_hp, 100, PURPLE, "DROIDE MUERTE")

        # Instrucción
        if not self.battle_over:
            hint = self.font_sm.render("Z / J / ENTER → ¡ATACAR!", True, YELLOW)
            surf.blit(hint, hint.get_rect(center=(W//2, 550)))

            # Cooldown visual
            if self.player_attack_timer > 0:
                cd = self.font_sm.render(
                    f"Recargando... {self.player_attack_timer//10+1}",
                    True, GREY)
                surf.blit(cd, cd.get_rect(center=(W//2, 568)))

        # Resultado
        if self.battle_over:
            overlay = pygame.Surface((W, 100), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surf.blit(overlay, (0, H//2 - 50))

            if self.winner == 'player':
                txt = self.font_big.render("¡VICTORIA!", True, GOLD)
                sub = self.font.render("¡La Muerte Negra ha sido derrotada!", True, WHITE)
            else:
                txt = self.font_big.render("DERROTA...", True, RED)
                sub = self.font.render("Reintentando en un momento...", True, GREY)

            surf.blit(txt, txt.get_rect(center=(W//2, H//2 - 20)))
            surf.blit(sub, sub.get_rect(center=(W//2, H//2 + 25)))

    def _draw_hp_bar(self, surf, x, y, hp, max_hp, color, label):
        bw = W//2 - 50
        bh = 24

        font = pygame.font.SysFont('Arial Black', 13)
        lbl = font.render(label, True, WHITE)
        surf.blit(lbl, (x, y - 16))

        pygame.draw.rect(surf, DARK_GREY, (x, y, bw, bh), border_radius=4)
        fill = int(bw * max(0, hp) / max_hp)
        if fill > 0:
            pygame.draw.rect(surf, color, (x, y, fill, bh), border_radius=4)
            pygame.draw.rect(surf, lighter(color, 40), (x, y, fill, bh//2), border_radius=4)
        pygame.draw.rect(surf, WHITE, (x, y, bw, bh), 2, border_radius=4)

        hp_txt = font.render(f"{max(0, hp)}%", True, WHITE)
        surf.blit(hp_txt, (x + bw//2 - hp_txt.get_width()//2, y + 4))


# ─────────────────────────────────────────────
#  PANTALLA DE VICTORIA
# ─────────────────────────────────────────────
class VictoryScene:
    def __init__(self):
        self.font_big  = pygame.font.SysFont('Impact', 60)
        self.font      = pygame.font.SysFont('Arial Black', 22)
        self.font_sm   = pygame.font.SysFont('Arial', 16)
        self.frame = 0
        self.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(120)]
        self.confetti = [(random.randint(0, W), random.randint(-H, 0),
                         random.choice([RED, BLUE, GREEN, ORANGE, YELLOW, PURPLE]),
                         random.uniform(-1, 1), random.uniform(1, 4))
                        for _ in range(80)]

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
            if ny > H + 20:
                ny = -20
                nx = random.randint(0, W)
            new.append((nx, ny, c, vx, vy))
        self.confetti = new

    def draw(self, surf):
        surf.fill(SPACE_BG)
        for sx, sy in self.stars:
            pygame.draw.circle(surf, STAR_COLOR, (sx, sy), 1)

        # Confetti
        for x, y, c, _, _ in self.confetti:
            pygame.draw.rect(surf, c, (int(x)-3, int(y)-3, 6, 6), border_radius=1)

        # Personajes celebrando
        for i, (ct, d) in enumerate([(OBI_WAN, 1), (DARTH_VADER, -1), (LUKE, 1)]):
            cx = 200 + i * 280
            draw_minifigure(surf, cx, 430, ct, d, 'idle', self.frame)

        # Título
        _draw_lego_text(surf,
            pygame.font.SysFont('Impact', 60),
            "¡NIVEL COMPLETADO!", W//2, 150, GOLD, BLACK)

        lines = [
            "¡La Muerte Negra ha sido detenida... por ahora!",
            "",
            "Darth Vader: 'Impresionante, Kenobi.'",
            "Obi-Wan: 'No esperaba decirlo, pero... bien hecho, Vader.'",
            "",
            "La historia continúa en el próximo nivel...",
        ]
        font = pygame.font.SysFont('Arial', 18)
        for i, line in enumerate(lines):
            t = font.render(line, True, WHITE if line else WHITE)
            surf.blit(t, t.get_rect(center=(W//2, 270 + i * 28)))

        if (self.frame // 30) % 2 == 0:
            hint = self.font_sm.render("ENTER / ESPACIO → Menú principal", True, YELLOW)
            surf.blit(hint, hint.get_rect(center=(W//2, 575)))


# ─────────────────────────────────────────────
#  Utilidad: texto con borde negro (estilo Lego)
# ─────────────────────────────────────────────
def _draw_lego_text(surf, font, text, cx, cy, color, shadow_color):
    for dx, dy in [(-3, 3), (3, 3), (-3, -3), (3, -3), (0, 4)]:
        s = font.render(text, True, shadow_color)
        surf.blit(s, s.get_rect(center=(cx + dx, cy + dy)))
    t = font.render(text, True, color)
    surf.blit(t, t.get_rect(center=(cx, cy)))
