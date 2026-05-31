# LEGO Story - Entidades del juego
import pygame
import random
import math
from settings import *
from draw_utils import draw_minifigure, draw_lego_piece, draw_gold_brick, draw_stud, draw_lego_brick


class Platform:
    def __init__(self, x, y, w, h, color=DARK_GREY):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, surf, cam_x):
        rx = self.rect.x - cam_x
        draw_lego_brick(surf, rx, self.rect.y, self.rect.w, self.rect.h, self.color)


class Player:
    def __init__(self, x, y, char_type=OBI_WAN):
        self.char_type = char_type
        self.rect = pygame.Rect(x, y, 20, 44)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.direction = 1
        self.state = 'idle'
        self.frame = 0
        self.hp = 3
        self.max_hp = 3
        self.attack_timer = 0
        self.inv_timer = 0     # invencibilidad tras daño
        self.pieces = 0
        self.studs = 0
        self.gold_bricks = 0
        self.dead = False
        self.jump_count = 0

    def handle_input(self, keys):
        if self.dead:
            return
        # Movimiento horizontal
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.direction = 1

        # Salto
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            if self.on_ground:
                self.vy = JUMP_VEL
                self.on_ground = False
                self.jump_count = 1

        # Ataque
        if (keys[pygame.K_z] or keys[pygame.K_j]) and self.attack_timer <= 0:
            self.attack_timer = 20
            self.state = 'attack'

    def update(self, platforms):
        if self.dead:
            return

        # Física
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL)

        self.rect.x += int(self.vx)
        self._collide_x(platforms)

        self.rect.y += int(self.vy)
        self.on_ground = False
        self._collide_y(platforms)

        # Límite inferior (no caer al vacío)
        if self.rect.top > H + 50:
            self._take_damage()
            self.rect.x = 100
            self.rect.y = 400
            self.vy = 0

        # Límite izquierdo
        if self.rect.left < 0:
            self.rect.left = 0

        # Timers
        self.frame += 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.state = 'attack'
        elif self.vx != 0:
            self.state = 'walk'
        elif not self.on_ground:
            self.state = 'jump'
        else:
            self.state = 'idle'

        if self.inv_timer > 0:
            self.inv_timer -= 1

    def _collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right
                self.vx = 0

    def _collide_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                    self.vy = 0

    def get_attack_rect(self):
        """Rectángulo de golpe del sable."""
        if self.attack_timer <= 0:
            return None
        if self.direction == 1:
            return pygame.Rect(self.rect.right, self.rect.top + 10, 28, 16)
        else:
            return pygame.Rect(self.rect.left - 28, self.rect.top + 10, 28, 16)

    def _take_damage(self):
        if self.inv_timer > 0:
            return
        self.hp -= 1
        self.inv_timer = 90
        if self.hp <= 0:
            self.dead = True

    def collect_piece(self, piece):
        self.pieces += 1
        self.studs += 50

    def collect_gold(self):
        self.gold_bricks += 1
        self.studs += 500

    def collect_stud(self, value):
        self.studs += value

    def draw(self, surf, cam_x):
        if self.dead:
            return
        screen_x = self.rect.centerx - cam_x
        screen_y = self.rect.bottom

        # Parpadeo al recibir daño
        if self.inv_timer > 0 and (self.inv_timer // 6) % 2 == 0:
            return

        draw_minifigure(surf, screen_x, screen_y,
                        self.char_type, self.direction, self.state, self.frame)


class Stormtrooper:
    def __init__(self, x, y, patrol_dist=100):
        self.rect = pygame.Rect(x, y, 18, 44)
        self.vx = 1.5
        self.vy = 0.0
        self.direction = 1
        self.state = 'walk'
        self.frame = 0
        self.hp = 2
        self.start_x = x
        self.patrol_dist = patrol_dist
        self.on_ground = False
        self.alive = True
        self.death_timer = 0
        self.stud_drop = []
        self.hit_flash = 0

    def update(self, platforms, player_attack_rect):
        if not self.alive:
            self.death_timer += 1
            return

        # Patrulla
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL)

        if abs(self.rect.x - self.start_x) > self.patrol_dist:
            self.vx *= -1
            self.direction = int(self.vx / abs(self.vx))

        self.rect.x += int(self.vx)
        self._collide_x(platforms)
        self.rect.y += int(self.vy)
        self.on_ground = False
        self._collide_y(platforms)

        self.frame += 1
        self.state = 'walk'
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Recibir ataque
        if player_attack_rect and self.rect.colliderect(player_attack_rect):
            self._hit()

    def _hit(self):
        self.hp -= 1
        self.hit_flash = 10
        if self.hp <= 0:
            self.alive = False
            # Soltar studs
            for _ in range(3):
                self.stud_drop.append(
                    FlyingStud(self.rect.centerx, self.rect.centery, 100)
                )

    def _collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                self.vx *= -1
                self.direction *= -1
                if self.vx > 0:
                    self.rect.left = p.rect.right
                else:
                    self.rect.right = p.rect.left

    def _collide_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                    self.vy = 0

    def draw(self, surf, cam_x):
        sx = self.rect.centerx - cam_x
        sy = self.rect.bottom

        if not self.alive:
            if self.death_timer < 40:
                # Explosión en piezas
                for i in range(6):
                    angle = i * 60 + self.death_timer * 5
                    px = sx + int(math.cos(math.radians(angle)) * self.death_timer * 1.5)
                    py = sy - 20 + int(math.sin(math.radians(angle)) * self.death_timer * 1.5)
                    c = random.choice([WHITE, GREY, DARK_GREY])
                    pygame.draw.rect(surf, c, (px-3, py-3, 6, 6), border_radius=1)
            return

        draw_minifigure(surf, sx, sy, STORMTROOPER,
                        self.direction, self.state, self.frame)

        # Flash de golpe
        if self.hit_flash > 0:
            flash = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 120))
            surf.blit(flash, (sx - self.rect.w//2, sy - self.rect.h))


class LegoPiece:
    def __init__(self, x, y, color=None):
        self.rect = pygame.Rect(x, y, 16, 12)
        self.color = color or random.choice([RED, BLUE, GREEN, ORANGE, YELLOW, TAN])
        self.collected = False
        self.float_offset = random.random() * math.pi * 2
        self.frame = 0

    def update(self):
        self.frame += 1

    def draw(self, surf, cam_x):
        if self.collected:
            return
        sx = self.rect.x - cam_x
        sy = self.rect.y + int(math.sin(self.frame * 0.05 + self.float_offset) * 4)
        draw_lego_piece(surf, sx, sy, self.color)

    def check_collect(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            return True
        return False


class GoldBrick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 22, 14)
        self.collected = False
        self.frame = 0

    def update(self):
        self.frame += 1

    def draw(self, surf, cam_x):
        if self.collected:
            return
        sx = self.rect.x - cam_x
        sy = self.rect.y + int(math.sin(self.frame * 0.04) * 5)
        draw_gold_brick(surf, sx, sy, self.frame)
        # Rayos dorados
        if self.frame % 30 < 5:
            for angle in range(0, 360, 45):
                ex = sx + 10 + int(math.cos(math.radians(angle)) * 14)
                ey = sy + 6 + int(math.sin(math.radians(angle)) * 14)
                pygame.draw.line(surf, GOLD, (sx+10, sy+6), (ex, ey), 1)

    def check_collect(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            return True
        return False


class FlyingStud:
    """Stud que vuela hacia el jugador tras matar enemigo."""
    def __init__(self, x, y, value=10):
        self.x = float(x)
        self.y = float(y)
        self.value = value
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.collected = False
        self.life = 120

    def update(self, player):
        if self.collected:
            return
        # Gravedad inicial luego atracción al jugador
        self.life -= 1
        if self.life > 80:
            self.vy += 0.3
        else:
            # Atracción magnética
            dx = player.rect.centerx - self.x
            dy = player.rect.centery - self.y
            dist = max(1, math.hypot(dx, dy))
            self.vx += dx / dist * 2
            self.vy += dy / dist * 2
            self.vx *= 0.9
            self.vy *= 0.9

        self.x += self.vx
        self.y += self.vy

        if pygame.Rect(self.x-6, self.y-6, 12, 12).colliderect(player.rect) or self.life <= 0:
            if not self.collected:
                self.collected = True
                if self.life > 0:
                    player.collect_stud(self.value)

    def draw(self, surf, cam_x):
        if self.collected:
            return
        draw_stud(surf, int(self.x - cam_x), int(self.y), self.value)
