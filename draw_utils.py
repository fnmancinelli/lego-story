# LEGO Story - Funciones de dibujo estilo Lego
import pygame
import math
from settings import *


def lighter(color, amt=40):
    return tuple(min(255, c + amt) for c in color)


def darker(color, amt=40):
    return tuple(max(0, c - amt) for c in color)


def draw_lego_brick(surf, x, y, w, h, color):
    """Dibuja un ladrillo Lego con studs arriba y efecto 3D."""
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, lighter(color, 50), rect, 2)
    # Sombra derecha/abajo
    pygame.draw.line(surf, darker(color, 50), (x+w-1, y+2), (x+w-1, y+h-1), 2)
    pygame.draw.line(surf, darker(color, 50), (x+2, y+h-1), (x+w-1, y+h-1), 2)
    # Divisiones de ladrillo cada 16px
    for sx in range(x+16, x+w, 16):
        pygame.draw.line(surf, darker(color, 30), (sx, y+2), (sx, y+h-2), 1)
    # Studs (círculos en la parte superior del ladrillo)
    stud_y = y - 5
    for sx in range(x+8, x+w, 16):
        pygame.draw.ellipse(surf, lighter(color, 30), (sx-5, stud_y, 10, 8))
        pygame.draw.ellipse(surf, darker(color, 20), (sx-5, stud_y, 10, 8), 1)


def draw_background(surf, cam_x, stars):
    """Fondo espacial Death Star con estrellas parallax."""
    surf.fill(SPACE_BG)
    # Estrellas (parallax lento)
    for sx, sy in stars:
        px = int((sx - cam_x * 0.1) % W)
        pygame.draw.circle(surf, STAR_COLOR, (px, sy), 1)
    # Panel de pared Death Star (ladrillo oscuro en el fondo)
    for row in range(0, H, 48):
        offset = 8 if (row // 48) % 2 else 0
        for col in range(-16 + offset, W + 48, 48):
            bx = int(col - (cam_x * 0.3) % 48)
            pygame.draw.rect(surf, (30, 35, 40), (bx, row, 46, 46), 1)


def draw_minifigure(surf, cx, by, char_type, direction=1, state='idle', frame=0):
    """
    Dibuja una minifigura Lego.
    cx = centro X, by = base Y (pies)
    direction: 1=derecha, -1=izquierda
    state: 'idle','walk','jump','attack','dead'
    """

    # Config por personaje
    cfgs = {
        OBI_WAN: dict(
            body=TAN, legs=BROWN, head=YELLOW,
            hair=(210, 200, 180), beard=True,
            saber=SABER_BLUE, helmet=None),
        DARTH_VADER: dict(
            body=BLACK, legs=BLACK, head=BLACK,
            hair=None, beard=False,
            saber=SABER_RED, helmet='vader'),
        LUKE: dict(
            body=(200, 180, 140), legs=GREY, head=YELLOW,
            hair=(180, 140, 80), beard=False,
            saber=SABER_GREEN, helmet=None),
        YODA: dict(
            body=BROWN, legs=BROWN, head=(160, 190, 120),
            hair=(200, 200, 190), beard=True,
            saber=SABER_GREEN, helmet='yoda'),
        STORMTROOPER: dict(
            body=WHITE, legs=WHITE, head=WHITE,
            hair=None, beard=False,
            saber=None, helmet='trooper'),
        MUERTE_NEGRA: dict(
            body=PURPLE, legs=BLACK, head=BLACK,
            hair=None, beard=False,
            saber=SABER_PURPLE, helmet='muerte'),
    }
    cfg = cfgs.get(char_type, cfgs[OBI_WAN])

    # Dimensiones
    LH = 14   # altura piernas
    LW = 7    # ancho pierna
    BH = 16   # altura cuerpo
    BW = 16   # ancho cuerpo
    RH = 9    # radio cabeza
    AW = 4    # ancho brazo
    AH = 11   # altura brazo

    lx = cx - BW // 2  # left X del cuerpo

    # Animación caminar
    la, ra = 0, 0  # left/right arm angle
    ll, rl = 0, 0  # left/right leg offset
    if state == 'walk':
        t = frame * 0.25
        ll = int(math.sin(t) * 4)
        rl = int(math.sin(t + math.pi) * 4)
        la = int(math.sin(t + math.pi) * 5)
        ra = int(math.sin(t) * 5)

    if state == 'dead':
        # Cae al lado
        rotated = pygame.Surface((50, 50), pygame.SRCALPHA)
        draw_minifigure(rotated, 25, 40, char_type, direction, 'idle', 0)
        rotated = pygame.transform.rotate(rotated, 90 * direction)
        surf.blit(rotated, (cx - 25, by - 30))
        return

    # --- PIERNAS ---
    leg_color = cfg['legs']
    # Pierna izquierda
    pygame.draw.rect(surf, leg_color, (lx, by - LH + ll, LW, LH - abs(ll)), border_radius=2)
    # Pierna derecha
    pygame.draw.rect(surf, leg_color, (lx + LW + 2, by - LH + rl, LW, LH - abs(rl)), border_radius=2)
    # Separador cadera
    pygame.draw.rect(surf, darker(leg_color, 20), (lx, by - LH - 2, BW, 4))

    # --- CUERPO ---
    body_color = cfg['body']
    pygame.draw.rect(surf, body_color, (lx, by - LH - BH, BW, BH), border_radius=3)
    # Detalle pecho
    pygame.draw.line(surf, lighter(body_color, 20),
                     (lx + 2, by - LH - BH + 4), (lx + BW - 2, by - LH - BH + 4), 1)
    # Logo o emblema
    if char_type == DARTH_VADER:
        pygame.draw.rect(surf, DARK_GREY, (lx+4, by-LH-BH+7, 8, 5), border_radius=1)
    elif char_type == OBI_WAN:
        pygame.draw.line(surf, darker(body_color, 30), (lx+5, by-LH-5), (lx+11, by-LH-5), 1)

    # --- BRAZOS ---
    arm_y = by - LH - BH + 2
    attack_ext = 5 if state == 'attack' else 0

    if direction == 1:
        # Brazo izquierdo (atrás)
        pygame.draw.rect(surf, body_color,
                         (lx - AW, arm_y + la, AW, AH), border_radius=2)
        pygame.draw.circle(surf, YELLOW, (lx - AW//2, arm_y + AH + la), 3)
        # Brazo derecho (adelante, con saber)
        pygame.draw.rect(surf, body_color,
                         (lx + BW, arm_y - attack_ext + ra, AW, AH + attack_ext), border_radius=2)
        hand_x = lx + BW + AW - 1
        hand_y = arm_y + AH - attack_ext + ra
        pygame.draw.circle(surf, YELLOW, (hand_x, hand_y), 3)
        # Saber
        if cfg['saber']:
            _draw_saber(surf, hand_x, hand_y, direction, cfg['saber'], state)
    else:
        # Espejo
        pygame.draw.rect(surf, body_color,
                         (lx + BW, arm_y + la, AW, AH), border_radius=2)
        pygame.draw.circle(surf, YELLOW, (lx + BW + AW//2, arm_y + AH + la), 3)
        pygame.draw.rect(surf, body_color,
                         (lx - AW, arm_y - attack_ext + ra, AW, AH + attack_ext), border_radius=2)
        hand_x = lx - 1
        hand_y = arm_y + AH - attack_ext + ra
        pygame.draw.circle(surf, YELLOW, (hand_x, hand_y), 3)
        if cfg['saber']:
            _draw_saber(surf, hand_x, hand_y, direction, cfg['saber'], state)

    # --- CABEZA ---
    head_cy = by - LH - BH - RH - 1
    _draw_head(surf, cx, head_cy, RH, cfg, char_type)

    # Stud encima de la cabeza
    pygame.draw.ellipse(surf, lighter(cfg['head'], 40), (cx-3, head_cy - RH - 4, 7, 6))
    pygame.draw.ellipse(surf, darker(cfg['head'], 20), (cx-3, head_cy - RH - 4, 7, 6), 1)


def _draw_saber(surf, hx, hy, direction, color, state):
    length = 26 if state == 'attack' else 22
    glow = lighter(color, 60)
    dx = direction * length
    # Brillo exterior
    pygame.draw.line(surf, darker(color, 20), (hx, hy), (hx + dx, hy - 2), 5)
    # Color principal
    pygame.draw.line(surf, color, (hx, hy), (hx + dx, hy - 2), 3)
    # Centro blanco brillante
    pygame.draw.line(surf, glow, (hx, hy), (hx + dx, hy - 2), 1)


def _draw_head(surf, cx, cy, r, cfg, char_type):
    helmet = cfg.get('helmet')

    if helmet == 'vader':
        # Casco icónico Vader
        pygame.draw.ellipse(surf, BLACK, (cx - r - 2, cy - r - 4, (r+2)*2, r*2 + 6))
        # Faceplate trapezoidal
        pts = [(cx-r, cy), (cx-r+3, cy+r+2), (cx+r-3, cy+r+2), (cx+r, cy)]
        pygame.draw.polygon(surf, BLACK, pts)
        # Lentes grises
        pygame.draw.ellipse(surf, DARK_GREY, (cx-r//2-2, cy-2, 7, 5))
        pygame.draw.ellipse(surf, DARK_GREY, (cx+1, cy-2, 7, 5))
        # Respirador
        for i in range(3):
            pygame.draw.rect(surf, DARK_GREY, (cx - 5 + i*4, cy + r - 1, 3, 3))

    elif helmet == 'trooper':
        # Casco Stormtrooper
        pygame.draw.ellipse(surf, WHITE, (cx-r, cy-r//2, r*2, r*2 + 3))
        # Lentes negros
        pygame.draw.ellipse(surf, BLACK, (cx-r//2-1, cy, 6, 5))
        pygame.draw.ellipse(surf, BLACK, (cx+1, cy, 6, 5))
        # Rejilla ventilación
        for i in range(3):
            pygame.draw.line(surf, GREY, (cx-4+i*3, cy+r+1), (cx-4+i*3, cy+r+4), 1)

    elif helmet == 'yoda':
        # Cabeza verde de Yoda con orejas
        pygame.draw.circle(surf, cfg['head'], (cx, cy), r)
        # Orejas grandes
        pygame.draw.ellipse(surf, cfg['head'], (cx - r - 6, cy - 2, 8, 14))
        pygame.draw.ellipse(surf, cfg['head'], (cx + r - 2, cy - 2, 8, 14))
        # Ojos grandes
        pygame.draw.circle(surf, darker(cfg['head'], 60), (cx-3, cy-1), 2)
        pygame.draw.circle(surf, darker(cfg['head'], 60), (cx+3, cy-1), 2)
        # Pelo blanco escaso
        pygame.draw.arc(surf, WHITE, (cx-r+1, cy-r, r*2-2, r), 0, math.pi, 2)

    elif helmet == 'muerte':
        # La Muerte Negra - calavera con capucha
        # Capucha
        pygame.draw.ellipse(surf, BLACK, (cx-r-3, cy-r-6, (r+3)*2, r*2+8))
        # Calavera
        pygame.draw.circle(surf, (200, 200, 200), (cx, cy), r-1)
        # Ojos vacíos (púrpura brillante)
        pygame.draw.ellipse(surf, PURPLE, (cx-r//2-1, cy-2, 7, 6))
        pygame.draw.ellipse(surf, PURPLE, (cx+1, cy-2, 7, 6))
        pygame.draw.ellipse(surf, lighter(PURPLE, 80), (cx-r//2, cy-1, 5, 4))
        pygame.draw.ellipse(surf, lighter(PURPLE, 80), (cx+2, cy-1, 5, 4))
        # Mandíbula
        pygame.draw.line(surf, DARK_GREY, (cx-4, cy+r-3), (cx+4, cy+r-3), 2)
        for i in range(-3, 4, 2):
            pygame.draw.line(surf, DARK_GREY, (cx+i, cy+r-3), (cx+i, cy+r), 1)

    else:
        # Cabeza normal amarilla
        pygame.draw.circle(surf, cfg['head'], (cx, cy), r)
        # Ojos
        pygame.draw.circle(surf, BLACK, (cx-3, cy-1), 1)
        pygame.draw.circle(surf, BLACK, (cx+3, cy-1), 1)
        # Sonrisa
        pygame.draw.arc(surf, BLACK, pygame.Rect(cx-4, cy, 8, 5), math.pi, 0, 1)

        if cfg.get('hair'):
            hair = cfg['hair']
            # Pelo en la parte superior
            pygame.draw.ellipse(surf, hair, (cx-r+1, cy-r, (r-1)*2, r))
        if cfg.get('beard'):
            pygame.draw.ellipse(surf, cfg.get('hair', GREY), (cx-4, cy+r-3, 8, 5))


def draw_lego_piece(surf, x, y, color, size=14):
    """Dibuja una pieza Lego coleccionable."""
    # Cuerpo del ladrillo 2x1
    pygame.draw.rect(surf, color, (x, y, size, size//2 + 2), border_radius=2)
    pygame.draw.rect(surf, lighter(color, 40), (x, y, size, size//2 + 2), 1)
    # Studs encima
    for i in range(2):
        sx = x + 3 + i * 7
        pygame.draw.ellipse(surf, lighter(color, 30), (sx, y-4, 6, 5))
        pygame.draw.ellipse(surf, darker(color, 10), (sx, y-4, 6, 5), 1)
    # Brillo coleccionable
    pygame.draw.circle(surf, WHITE, (x+2, y+2), 2)


def draw_gold_brick(surf, x, y, pulse=0):
    """Dibuja un ladrillo dorado especial con efecto de brillo."""
    glow = int(abs(math.sin(pulse * 0.05)) * 30)
    color = (min(255, GOLD[0]+glow), min(255, GOLD[1]+glow//2), 0)
    pygame.draw.rect(surf, color, (x, y, 20, 12), border_radius=2)
    pygame.draw.rect(surf, lighter(color, 60), (x, y, 20, 12), 1)
    # Studs
    for i in range(2):
        pygame.draw.ellipse(surf, lighter(color, 40), (x+3+i*9, y-4, 7, 6))
    # Destello
    if glow > 15:
        pygame.draw.line(surf, WHITE, (x+1, y+1), (x+5, y+5), 1)


def draw_stud(surf, x, y, value=10):
    """Dibuja una moneda stud."""
    colors = {10: GREY, 100: GOLD, 1000: BLUE, 10000: PURPLE}
    c = colors.get(value, GREY)
    pygame.draw.circle(surf, c, (x, y), 6)
    pygame.draw.circle(surf, lighter(c, 60), (x, y), 6, 1)
    pygame.draw.circle(surf, lighter(c, 80), (x-2, y-2), 2)


def draw_droid(surf, cx, by, droid_type, hp_ratio=1.0, frame=0):
    """
    Dibuja un droide gigante de Lego/Star Wars.
    droid_type: 'alliance' o 'muerte'
    """
    # Tamaño del droide
    W = 120
    H = 180

    if droid_type == 'alliance':
        main_color = BLUE
        accent = YELLOW
        eye_color = SABER_BLUE
    else:
        main_color = DARK_GREY
        accent = PURPLE
        eye_color = SABER_PURPLE

    # Respiración/idle animation
    bob = int(math.sin(frame * 0.08) * 3)
    body_y = by - H + bob

    # --- PIERNAS ---
    leg_w = 28
    leg_h = 60
    pygame.draw.rect(surf, darker(main_color, 20),
                     (cx - W//2 + 5, by - leg_h, leg_w, leg_h), border_radius=4)
    pygame.draw.rect(surf, darker(main_color, 20),
                     (cx + W//2 - leg_w - 5, by - leg_h, leg_w, leg_h), border_radius=4)
    # Pies
    pygame.draw.rect(surf, darker(main_color, 30),
                     (cx - W//2, by - 12, 40, 12), border_radius=3)
    pygame.draw.rect(surf, darker(main_color, 30),
                     (cx + W//2 - 40, by - 12, 40, 12), border_radius=3)

    # --- TORSO ---
    torso_rect = pygame.Rect(cx - W//2 + 5, body_y + 60, W - 10, 90)
    pygame.draw.rect(surf, main_color, torso_rect, border_radius=8)
    pygame.draw.rect(surf, lighter(main_color, 30), torso_rect, 2)
    # Detalle de ladrillo en el torso
    for i in range(1, 3):
        pygame.draw.line(surf, darker(main_color, 20),
                         (torso_rect.x+5, torso_rect.y+i*28),
                         (torso_rect.right-5, torso_rect.y+i*28), 1)

    # Panel del pecho
    panel_rect = pygame.Rect(cx-30, body_y+75, 60, 40)
    pygame.draw.rect(surf, darker(main_color, 30), panel_rect, border_radius=4)
    # Luces del panel
    for i, lc in enumerate([(255,50,50), (50,255,50), (50,50,255), accent]):
        pygame.draw.circle(surf, lc, (cx-20+i*14, body_y+88), 4)
        if int(frame*0.15+i) % 3 == 0:
            pygame.draw.circle(surf, lighter(lc, 80), (cx-20+i*14, body_y+88), 2)

    # --- BRAZOS ---
    arm_w = 20
    arm_h = 80
    # Brazo izquierdo
    arm_angle = int(math.sin(frame * 0.06) * 8)
    pygame.draw.rect(surf, darker(main_color, 10),
                     (cx - W//2 - arm_w + 5, body_y + 62 + arm_angle, arm_w, arm_h), border_radius=5)
    # Cañón brazo izquierdo
    pygame.draw.rect(surf, darker(main_color, 30),
                     (cx - W//2 - arm_w - 5, body_y + 62 + arm_h//2, 14, 10), border_radius=3)
    # Brazo derecho
    pygame.draw.rect(surf, darker(main_color, 10),
                     (cx + W//2 - 5, body_y + 62 - arm_angle, arm_w, arm_h), border_radius=5)
    # Cañón brazo derecho
    pygame.draw.rect(surf, darker(main_color, 30),
                     (cx + W//2 + 5, body_y + 62 + arm_h//2 - arm_angle, 14, 10), border_radius=3)

    # --- CABEZA ---
    head_w = 80
    head_h = 65
    head_x = cx - head_w//2
    head_y = body_y + bob - 5
    pygame.draw.rect(surf, main_color, (head_x, head_y, head_w, head_h), border_radius=10)
    pygame.draw.rect(surf, lighter(main_color, 40), (head_x, head_y, head_w, head_h), 2)

    # Visera / visor
    visor_rect = pygame.Rect(head_x+8, head_y+12, head_w-16, 22)
    pygame.draw.rect(surf, BLACK, visor_rect, border_radius=5)
    # Ojos
    pygame.draw.ellipse(surf, eye_color, (cx-20, head_y+16, 18, 14))
    pygame.draw.ellipse(surf, eye_color, (cx+2, head_y+16, 18, 14))
    pygame.draw.ellipse(surf, lighter(eye_color, 80), (cx-16, head_y+18, 8, 7))
    pygame.draw.ellipse(surf, lighter(eye_color, 80), (cx+6, head_y+18, 8, 7))

    # Antenas
    pygame.draw.line(surf, GREY, (cx-20, head_y), (cx-30, head_y-20), 2)
    pygame.draw.circle(surf, accent, (cx-30, head_y-20), 4)
    pygame.draw.line(surf, GREY, (cx+20, head_y), (cx+30, head_y-20), 2)
    pygame.draw.circle(surf, accent, (cx+30, head_y-20), 4)

    # Studs en la cabeza (detalle Lego)
    for i in range(3):
        sx = head_x + 10 + i * 25
        pygame.draw.ellipse(surf, lighter(main_color, 20), (sx, head_y-5, 14, 10))

    # Daño (grietas si hp bajo)
    if hp_ratio < 0.4:
        pygame.draw.line(surf, darker(main_color, 60),
                         (cx-10, body_y+65), (cx+20, body_y+100), 2)
        pygame.draw.line(surf, darker(main_color, 60),
                         (cx+5, head_y+20), (cx-15, head_y+50), 2)


def draw_hud(surf, pieces, max_pieces, gold_bricks, studs, hp, max_hp):
    """Dibuja el HUD del juego."""
    # Panel superior semi-transparente
    hud_surf = pygame.Surface((W, 52), pygame.SRCALPHA)
    hud_surf.fill((10, 10, 30, 180))
    surf.blit(hud_surf, (0, 0))

    font_big = pygame.font.SysFont('Arial Black', 16, bold=True)
    font_sm = pygame.font.SysFont('Arial', 13)

    # Piezas recolectadas
    draw_lego_piece(surf, 12, 18, BLUE, 14)
    txt = font_big.render(f"{pieces}/{max_pieces}", True, WHITE)
    surf.blit(txt, (32, 16))

    # Studs
    draw_stud(surf, 140, 22, 100)
    txt = font_big.render(f"{studs:,}", True, GOLD)
    surf.blit(txt, (152, 14))

    # Ladrillo dorado
    draw_gold_brick(surf, 260, 16)
    txt = font_big.render(f"x{gold_bricks}", True, GOLD)
    surf.blit(txt, (285, 14))

    # Vida (corazones estilo Lego)
    for i in range(max_hp):
        hx = W - 28 - i * 26
        color = RED if i < hp else DARK_GREY
        pygame.draw.rect(surf, color, (hx, 12, 20, 20), border_radius=4)
        if i < hp:
            pygame.draw.rect(surf, lighter(RED, 40), (hx, 12, 20, 20), 2)
            pygame.draw.line(surf, lighter(RED, 60), (hx+3, 16), (hx+7, 16), 1)

    # Barra de piezas recolectadas (progreso hacia el droide)
    bar_x, bar_y = 12, 44
    bar_w = 200
    pygame.draw.rect(surf, DARK_GREY, (bar_x, bar_y, bar_w, 6), border_radius=3)
    fill = int(bar_w * min(pieces / max_pieces, 1.0))
    if fill > 0:
        pygame.draw.rect(surf, BLUE, (bar_x, bar_y, fill, 6), border_radius=3)
    pygame.draw.rect(surf, GREY, (bar_x, bar_y, bar_w, 6), 1, border_radius=3)
    hint = font_sm.render("PIEZAS DROIDE", True, GREY)
    surf.blit(hint, (bar_x + bar_w + 5, bar_y - 2))
