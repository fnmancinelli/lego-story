# LEGO Story - Funciones de dibujo estilo Lego
import pygame
import math
import random
from settings import *


def lighter(color, amt=40):
    return tuple(min(255, c + amt) for c in color)


def darker(color, amt=40):
    return tuple(max(0, c - amt) for c in color)


def draw_lego_brick(surf, x, y, w, h, color):
    """Ladrillo Lego con studs y efecto 3D."""
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, lighter(color, 50), rect, 2)
    pygame.draw.line(surf, darker(color, 50), (x+w-1, y+2), (x+w-1, y+h-1), 2)
    pygame.draw.line(surf, darker(color, 50), (x+2, y+h-1), (x+w-1, y+h-1), 2)
    for sx in range(x+16, x+w, 16):
        pygame.draw.line(surf, darker(color, 30), (sx, y+2), (sx, y+h-2), 1)
    stud_y = y - 5
    for sx in range(x+8, x+w, 16):
        pygame.draw.ellipse(surf, lighter(color, 30), (sx-5, stud_y, 10, 8))
        pygame.draw.ellipse(surf, darker(color, 20), (sx-5, stud_y, 10, 8), 1)


def draw_background(surf, cam_x, stars):
    surf.fill(SPACE_BG)
    for sx, sy in stars:
        px = int((sx - cam_x * 0.1) % W)
        pygame.draw.circle(surf, STAR_COLOR, (px, sy), 1)
    for row in range(0, H, 48):
        offset = 8 if (row // 48) % 2 else 0
        for col in range(-16 + offset, W + 48, 48):
            bx = int(col - (cam_x * 0.3) % 48)
            pygame.draw.rect(surf, (30, 35, 40), (bx, row, 46, 46), 1)


# ──────────────────────────────────────────────────────
#  MINIFIGURA LEGO  (escala 1.0 = tamaño original)
#  escala 1.6 por defecto → personajes más grandes
# ──────────────────────────────────────────────────────
def draw_minifigure(surf, cx, by, char_type, direction=1,
                    state='idle', frame=0, scale=1.6):
    S = scale

    # Dimensiones proporcionales a minifigura Lego real
    LH = int(18 * S)   # piernas
    LW = int(9  * S)
    BH = int(20 * S)   # cuerpo
    BW = int(20 * S)
    RH = int(11 * S)   # radio cabeza
    AW = int(5  * S)   # brazo
    AH = int(13 * S)

    cfgs = {
        OBI_WAN:      dict(body=TAN,   legs=BROWN, head=YELLOW,
                          hair=(210,200,180), beard=True,
                          saber=SABER_BLUE,   helmet=None),
        DARTH_VADER:  dict(body=BLACK, legs=BLACK, head=BLACK,
                          hair=None,          beard=False,
                          saber=SABER_RED,    helmet='vader'),
        LUKE:         dict(body=(200,180,140), legs=GREY, head=YELLOW,
                          hair=(185,148,85),  beard=False,
                          saber=SABER_GREEN,  helmet=None),
        YODA:         dict(body=BROWN, legs=BROWN, head=(145,175,110),
                          hair=(210,210,195), beard=True,
                          saber=SABER_GREEN,  helmet='yoda'),
        STORMTROOPER: dict(body=WHITE, legs=WHITE, head=WHITE,
                          hair=None,          beard=False,
                          saber=None,         helmet='trooper'),
        MUERTE_NEGRA: dict(body=PURPLE, legs=BLACK, head=BLACK,
                          hair=None,          beard=False,
                          saber=SABER_PURPLE, helmet='muerte'),
    }
    cfg = cfgs.get(char_type, cfgs[OBI_WAN])

    lx = cx - BW // 2

    # Animación caminar
    ll = rl = 0
    if state == 'walk':
        t = frame * 0.22
        ll = int(math.sin(t) * int(5*S))
        rl = int(math.sin(t + math.pi) * int(5*S))

    if state == 'dead':
        return

    # ── PIERNAS ──
    lc = cfg['legs']
    # Separación entre piernas = 2px
    pygame.draw.rect(surf, lc, (lx,           by - LH + ll, LW, LH - abs(ll)), border_radius=int(3*S))
    pygame.draw.rect(surf, lc, (lx + LW + int(2*S), by - LH + rl, LW, LH - abs(rl)), border_radius=int(3*S))
    # Detalle zapato
    shoe_c = darker(lc, 30)
    pygame.draw.rect(surf, shoe_c, (lx - int(1*S), by - int(4*S), LW + int(2*S), int(4*S)), border_radius=int(2*S))
    pygame.draw.rect(surf, shoe_c, (lx + LW + int(1*S), by - int(4*S), LW + int(2*S), int(4*S)), border_radius=int(2*S))
    # Cadera
    pygame.draw.rect(surf, darker(lc, 20), (lx, by - LH - int(3*S), BW, int(5*S)))

    # ── CUERPO ──
    bc = cfg['body']
    body_rect = pygame.Rect(lx, by - LH - BH, BW, BH)
    pygame.draw.rect(surf, bc, body_rect, border_radius=int(4*S))
    pygame.draw.rect(surf, lighter(bc, 25), body_rect, int(1*S), border_radius=int(4*S))

    # Detalle cinturón
    belt_y = by - LH - int(6*S)
    pygame.draw.rect(surf, darker(bc, 40), (lx + int(2*S), belt_y, BW - int(4*S), int(4*S)), border_radius=int(2*S))

    # Emblema pecho según personaje
    chest_y = by - LH - BH + int(6*S)
    if char_type == DARTH_VADER:
        pygame.draw.rect(surf, DARK_GREY, (lx + int(5*S), chest_y, int(10*S), int(7*S)), border_radius=int(2*S))
        for i in range(3):
            pygame.draw.circle(surf, [RED, (50,200,50), BLUE][i],
                               (lx + int(6*S) + i*int(3*S), chest_y + int(3*S)), int(1.5*S))
    elif char_type == OBI_WAN:
        pygame.draw.line(surf, darker(bc, 30),
                         (lx + int(4*S), chest_y + int(4*S)),
                         (lx + BW - int(4*S), chest_y + int(4*S)), int(1*S))
    elif char_type == LUKE:
        pygame.draw.rect(surf, WHITE, (lx + int(6*S), chest_y + int(2*S), int(8*S), int(5*S)), border_radius=int(2*S))

    # ── BRAZOS ──
    arm_y = by - LH - BH + int(3*S)
    atk = int(6*S) if state == 'attack' else 0

    if direction == 1:
        # Brazo izquierdo (atrás)
        pygame.draw.rect(surf, bc, (lx - AW, arm_y, AW, AH), border_radius=int(3*S))
        pygame.draw.circle(surf, YELLOW, (lx - AW//2, arm_y + AH), int(4*S))
        # Brazo derecho (adelante, con arma)
        pygame.draw.rect(surf, bc, (lx + BW, arm_y - atk, AW, AH + atk), border_radius=int(3*S))
        hx = lx + BW + AW - int(2*S)
        hy = arm_y + AH - atk
        pygame.draw.circle(surf, YELLOW, (hx, hy), int(4*S))
        if cfg['saber']:
            _draw_saber(surf, hx, hy, direction, cfg['saber'], state, S)
    else:
        pygame.draw.rect(surf, bc, (lx + BW, arm_y, AW, AH), border_radius=int(3*S))
        pygame.draw.circle(surf, YELLOW, (lx + BW + AW//2, arm_y + AH), int(4*S))
        pygame.draw.rect(surf, bc, (lx - AW, arm_y - atk, AW, AH + atk), border_radius=int(3*S))
        hx = lx - int(2*S)
        hy = arm_y + AH - atk
        pygame.draw.circle(surf, YELLOW, (hx, hy), int(4*S))
        if cfg['saber']:
            _draw_saber(surf, hx, hy, direction, cfg['saber'], state, S)

    # ── CABEZA ──
    head_cy = by - LH - BH - RH - int(2*S)
    _draw_head(surf, cx, head_cy, RH, cfg, char_type, S)

    # Stud encima de cabeza (icónico Lego)
    stud_c = lighter(cfg.get('hair') or cfg['head'], 40)
    pygame.draw.ellipse(surf, stud_c, (cx - int(4*S), head_cy - RH - int(5*S), int(8*S), int(7*S)))
    pygame.draw.ellipse(surf, darker(stud_c, 30), (cx - int(4*S), head_cy - RH - int(5*S), int(8*S), int(7*S)), 1)


def _draw_saber(surf, hx, hy, direction, color, state, S=1.0):
    length = int((30 if state == 'attack' else 26) * S)
    glow = lighter(color, 70)
    dx = direction * length
    # Hilt (mango)
    pygame.draw.rect(surf, DARK_GREY,
                     (hx if direction == 1 else hx - int(6*S), hy - int(2*S), int(6*S), int(5*S)),
                     border_radius=1)
    # Blade (hoja brillante)
    end_x = hx + dx
    pygame.draw.line(surf, darker(color, 30), (hx, hy), (end_x, hy - int(2*S)), int(5*S))
    pygame.draw.line(surf, color,             (hx, hy), (end_x, hy - int(2*S)), int(3*S))
    pygame.draw.line(surf, glow,              (hx, hy), (end_x, hy - int(2*S)), int(1*S))


def _draw_head(surf, cx, cy, r, cfg, char_type, S=1.0):
    helmet = cfg.get('helmet')

    if helmet == 'vader':
        # Casco icónico Vader en negro
        pygame.draw.ellipse(surf, BLACK,
                            (cx - r - int(3*S), cy - r - int(6*S),
                             (r + int(3*S))*2, r*2 + int(8*S)))
        pts = [(cx-r, cy), (cx-r+int(4*S), cy+r+int(3*S)),
               (cx+r-int(4*S), cy+r+int(3*S)), (cx+r, cy)]
        pygame.draw.polygon(surf, BLACK, pts)
        # Lentes plateados
        pygame.draw.ellipse(surf, DARK_GREY, (cx - int(8*S), cy, int(10*S), int(7*S)))
        pygame.draw.ellipse(surf, DARK_GREY, (cx + int(2*S), cy, int(10*S), int(7*S)))
        pygame.draw.ellipse(surf, lighter(DARK_GREY, 40), (cx - int(7*S), cy+int(1*S), int(6*S), int(4*S)))
        pygame.draw.ellipse(surf, lighter(DARK_GREY, 40), (cx + int(3*S), cy+int(1*S), int(6*S), int(4*S)))
        # Respirador
        for i in range(4):
            pygame.draw.rect(surf, DARK_GREY,
                             (cx - int(6*S) + i*int(3*S), cy + r, int(2*S), int(4*S)),
                             border_radius=1)
        pygame.draw.rect(surf, darker(DARK_GREY, 30),
                         (cx - int(8*S), cy + r - int(2*S), int(16*S), int(3*S)))

    elif helmet == 'trooper':
        # Stormtrooper - casco blanco redondeado
        pygame.draw.ellipse(surf, WHITE, (cx-r, cy-r//3, r*2, r*2+int(4*S)))
        # Barbilla
        pygame.draw.rect(surf, WHITE,   (cx - int(7*S), cy+r-int(3*S), int(14*S), int(6*S)), border_radius=int(3*S))
        # Lentes negros alargados
        pygame.draw.ellipse(surf, BLACK, (cx-r+int(2*S), cy+int(1*S), int(9*S), int(7*S)))
        pygame.draw.ellipse(surf, BLACK, (cx+int(1*S),   cy+int(1*S), int(9*S), int(7*S)))
        # Brillo en lentes
        pygame.draw.ellipse(surf, (60,60,80), (cx-r+int(3*S), cy+int(2*S), int(4*S), int(3*S)))
        pygame.draw.ellipse(surf, (60,60,80), (cx+int(2*S),   cy+int(2*S), int(4*S), int(3*S)))
        # Ventilación
        for i in range(3):
            pygame.draw.line(surf, GREY,
                             (cx-int(3*S)+i*int(3*S), cy+r+int(1*S)),
                             (cx-int(3*S)+i*int(3*S), cy+r+int(5*S)), 1)

    elif helmet == 'yoda':
        # Cabeza verde con orejas enormes
        pygame.draw.circle(surf, cfg['head'], (cx, cy), r)
        # Orejas grandes (característica de Yoda)
        ear_pts_l = [(cx-r, cy-int(2*S)), (cx-r-int(12*S), cy-int(8*S)),
                     (cx-r-int(10*S), cy+int(8*S)), (cx-r+int(2*S), cy+int(4*S))]
        ear_pts_r = [(cx+r, cy-int(2*S)), (cx+r+int(12*S), cy-int(8*S)),
                     (cx+r+int(10*S), cy+int(8*S)), (cx+r-int(2*S), cy+int(4*S))]
        pygame.draw.polygon(surf, cfg['head'], ear_pts_l)
        pygame.draw.polygon(surf, cfg['head'], ear_pts_r)
        pygame.draw.polygon(surf, darker(cfg['head'],20), ear_pts_l, 1)
        pygame.draw.polygon(surf, darker(cfg['head'],20), ear_pts_r, 1)
        # Ojos grandes sabios
        pygame.draw.circle(surf, darker(cfg['head'], 70), (cx-int(4*S), cy-int(1*S)), int(3*S))
        pygame.draw.circle(surf, darker(cfg['head'], 70), (cx+int(4*S), cy-int(1*S)), int(3*S))
        pygame.draw.circle(surf, lighter(cfg['head'],60), (cx-int(3*S), cy-int(2*S)), int(1*S))
        pygame.draw.circle(surf, lighter(cfg['head'],60), (cx+int(5*S), cy-int(2*S)), int(1*S))
        # Arrugas / pelo blanco escaso
        pygame.draw.arc(surf, (210,210,195),
                        pygame.Rect(cx-r+int(2*S), cy-r, r*2-int(4*S), r),
                        0, math.pi, int(3*S))

    elif helmet == 'muerte':
        # La Muerte Negra - calavera con capucha oscura
        pygame.draw.ellipse(surf, (40,30,60),
                            (cx-r-int(5*S), cy-r-int(8*S), (r+int(5*S))*2, r*2+int(12*S)))
        # Cráneo
        pygame.draw.circle(surf, (210, 210, 215), (cx, cy), r)
        # Cuencas oculares (púrpura brillante)
        pygame.draw.ellipse(surf, (80, 0, 100), (cx-r//2-int(2*S), cy-int(3*S), int(10*S), int(8*S)))
        pygame.draw.ellipse(surf, (80, 0, 100), (cx+int(1*S),       cy-int(3*S), int(10*S), int(8*S)))
        pygame.draw.ellipse(surf, PURPLE, (cx-r//2-int(1*S), cy-int(2*S), int(7*S), int(5*S)))
        pygame.draw.ellipse(surf, PURPLE, (cx+int(2*S),       cy-int(2*S), int(7*S), int(5*S)))
        pygame.draw.ellipse(surf, lighter(PURPLE,80), (cx-r//2, cy-int(1*S), int(4*S), int(3*S)))
        pygame.draw.ellipse(surf, lighter(PURPLE,80), (cx+int(3*S), cy-int(1*S), int(4*S), int(3*S)))
        # Mandíbula con dientes
        pygame.draw.line(surf, DARK_GREY,
                         (cx-int(6*S), cy+r-int(3*S)), (cx+int(6*S), cy+r-int(3*S)), int(2*S))
        for i in range(-2, 3):
            pygame.draw.rect(surf, WHITE,
                             (cx + i*int(3*S) - int(1*S), cy+r-int(3*S), int(2*S), int(4*S)))
        # Guadaña (accesorio)
        pygame.draw.line(surf, darker(GREY,20),
                         (cx+r, cy-int(4*S)), (cx+r+int(8*S), cy-int(14*S)), int(2*S))
        pygame.draw.ellipse(surf, GREY,
                            (cx+r+int(4*S), cy-int(16*S), int(8*S), int(6*S)))

    else:
        # Cabeza amarilla estándar
        pygame.draw.circle(surf, cfg['head'], (cx, cy), r)
        pygame.draw.circle(surf, darker(cfg['head'], 15), (cx, cy), r, 1)
        # Ojos con brillo
        pygame.draw.circle(surf, BLACK, (cx - int(4*S), cy - int(1*S)), int(2*S))
        pygame.draw.circle(surf, BLACK, (cx + int(4*S), cy - int(1*S)), int(2*S))
        pygame.draw.circle(surf, WHITE, (cx - int(3*S), cy - int(2*S)), int(1*S))
        pygame.draw.circle(surf, WHITE, (cx + int(5*S), cy - int(2*S)), int(1*S))
        # Sonrisa
        pygame.draw.arc(surf, BLACK,
                        pygame.Rect(cx-int(4*S), cy, int(9*S), int(6*S)),
                        math.pi, 0, int(1*S))

        if cfg.get('hair'):
            hair = cfg['hair']
            pygame.draw.ellipse(surf, hair,
                                (cx-r+int(1*S), cy-r, (r-int(1*S))*2, r))
            if char_type == LUKE:
                # Flequillo
                pygame.draw.ellipse(surf, hair,
                                    (cx-r+int(2*S), cy-int(2*S), int(8*S), int(5*S)))

        if cfg.get('beard'):
            pygame.draw.ellipse(surf, cfg.get('hair', GREY),
                                (cx-int(5*S), cy+r-int(4*S), int(10*S), int(6*S)))


# ──────────────────────────────────────────────────────
#  EFECTO FUERZA
# ──────────────────────────────────────────────────────
def draw_force_effect(surf, cx, cy, direction, timer, char_type):
    """Onda de la Fuerza emanando del personaje."""
    if timer <= 0:
        return
    t = 30 - timer  # 0..30
    alpha_val = max(0, 200 - t * 7)
    color = SABER_RED if char_type == DARTH_VADER else SABER_BLUE
    color_glow = lighter(color, 60)

    for ring in range(3):
        radius = int((t * 5 + ring * 15) * (1 + direction * 0.3))
        cx2 = cx + direction * int(t * 3)
        if radius <= 0:
            continue
        wave_surf = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
        a = max(0, alpha_val - ring * 50)
        pygame.draw.ellipse(wave_surf, (*color, a),
                            (0, radius//2, radius*2+4, radius+2), int(2+ring))
        surf.blit(wave_surf, (cx2 - radius - 2, cy - radius//2 - 1))


# ──────────────────────────────────────────────────────
#  DROIDES  (rediseñados según las fotos)
# ──────────────────────────────────────────────────────
def draw_droid(surf, cx, by, droid_type, hp_ratio=1.0, frame=0):
    if droid_type == 'alliance':
        _draw_droid_alliance(surf, cx, by, hp_ratio, frame)
    else:
        _draw_droid_muerte(surf, cx, by, hp_ratio, frame)


def _draw_droid_alliance(surf, cx, by, hp_ratio, frame):
    """
    Droide alianza - estilo Transformers/naranja robusto (foto 2).
    Proporciones más compactas, estilo Star Wars mech.
    """
    bob = int(math.sin(frame * 0.07) * 3)
    W2 = 100
    H2 = 160
    base_y = by + bob

    main_c  = ORANGE
    dark_c  = darker(ORANGE, 50)
    acc_c   = WHITE
    eye_c   = (60, 160, 255)

    # ── PIES / BOTAS ──
    # Pie izquierdo
    pygame.draw.rect(surf, dark_c,
                     (cx - W2//2 - 8, base_y - 18, 44, 18), border_radius=4)
    pygame.draw.rect(surf, darker(dark_c, 20),
                     (cx - W2//2 - 10, base_y - 8, 48, 8), border_radius=3)
    # Pie derecho
    pygame.draw.rect(surf, dark_c,
                     (cx + W2//2 - 36, base_y - 18, 44, 18), border_radius=4)
    pygame.draw.rect(surf, darker(dark_c, 20),
                     (cx + W2//2 - 38, base_y - 8, 48, 8), border_radius=3)

    # ── PIERNAS ──
    leg_w = 26
    leg_h = 55
    # Pierna izquierda (con detalle angular)
    leg_pts_l = [(cx-W2//2+2, base_y-18),
                 (cx-W2//2+2+leg_w, base_y-18),
                 (cx-W2//2+5+leg_w, base_y-18-leg_h),
                 (cx-W2//2+5, base_y-18-leg_h)]
    pygame.draw.polygon(surf, main_c, leg_pts_l)
    pygame.draw.polygon(surf, lighter(main_c, 20), leg_pts_l, 2)
    # Rodilla izquierda
    pygame.draw.rect(surf, dark_c,
                     (cx-W2//2+4, base_y-18-leg_h//2-8, leg_w-2, 16), border_radius=3)
    pygame.draw.rect(surf, acc_c,
                     (cx-W2//2+8, base_y-18-leg_h//2-5, leg_w-10, 10), border_radius=2)

    # Pierna derecha
    leg_pts_r = [(cx+W2//2-2, base_y-18),
                 (cx+W2//2-2-leg_w, base_y-18),
                 (cx+W2//2-5-leg_w, base_y-18-leg_h),
                 (cx+W2//2-5, base_y-18-leg_h)]
    pygame.draw.polygon(surf, main_c, leg_pts_r)
    pygame.draw.polygon(surf, lighter(main_c, 20), leg_pts_r, 2)
    pygame.draw.rect(surf, dark_c,
                     (cx+W2//2-4-leg_w+2, base_y-18-leg_h//2-8, leg_w-2, 16), border_radius=3)
    pygame.draw.rect(surf, acc_c,
                     (cx+W2//2-8-leg_w+2, base_y-18-leg_h//2-5, leg_w-10, 10), border_radius=2)

    torso_y = base_y - 18 - leg_h

    # ── TORSO ──
    torso_w = W2 - 4
    torso_h = 75
    torso_rect = pygame.Rect(cx - torso_w//2, torso_y - torso_h, torso_w, torso_h)
    pygame.draw.rect(surf, main_c, torso_rect, border_radius=8)
    pygame.draw.rect(surf, lighter(main_c, 30), torso_rect, 2, border_radius=8)

    # Detalle central blanco
    pygame.draw.rect(surf, acc_c,
                     (cx - 14, torso_y - torso_h + 10, 28, torso_h - 20),
                     border_radius=4)
    # Panel de luces
    for i, lc in enumerate([(255,60,60),(60,255,60),(60,60,255)]):
        pygame.draw.circle(surf, lc, (cx - 8 + i*8, torso_y - torso_h//2), 4)
        if int(frame * 0.1 + i) % 4 < 2:
            pygame.draw.circle(surf, WHITE, (cx - 8 + i*8, torso_y - torso_h//2), 2)

    # ── HOMBROS (armor plates angulares) ──
    # Hombro izquierdo
    sh_pts_l = [(cx-torso_w//2-2, torso_y-torso_h+5),
                (cx-torso_w//2-28, torso_y-torso_h+20),
                (cx-torso_w//2-28, torso_y-torso_h+55),
                (cx-torso_w//2-2, torso_y-torso_h+45)]
    pygame.draw.polygon(surf, main_c, sh_pts_l)
    pygame.draw.polygon(surf, lighter(main_c, 30), sh_pts_l, 2)
    # Hombro derecho
    sh_pts_r = [(cx+torso_w//2+2, torso_y-torso_h+5),
                (cx+torso_w//2+28, torso_y-torso_h+20),
                (cx+torso_w//2+28, torso_y-torso_h+55),
                (cx+torso_w//2+2, torso_y-torso_h+45)]
    pygame.draw.polygon(surf, main_c, sh_pts_r)
    pygame.draw.polygon(surf, lighter(main_c, 30), sh_pts_r, 2)

    # ── BRAZOS ──
    arm_w = 20
    arm_y = torso_y - torso_h + 20
    arm_h = 60
    arm_angle = int(math.sin(frame * 0.06) * 6)
    # Brazo izquierdo
    pygame.draw.rect(surf, darker(main_c, 20),
                     (cx-torso_w//2-arm_w-8, arm_y+arm_angle, arm_w, arm_h),
                     border_radius=5)
    # Puño / cañón
    pygame.draw.rect(surf, dark_c,
                     (cx-torso_w//2-arm_w-16, arm_y+arm_h//2+arm_angle, 16, 12),
                     border_radius=3)

    # Brazo derecho
    pygame.draw.rect(surf, darker(main_c, 20),
                     (cx+torso_w//2+8, arm_y-arm_angle, arm_w, arm_h),
                     border_radius=5)
    pygame.draw.rect(surf, dark_c,
                     (cx+torso_w//2+arm_w+8, arm_y+arm_h//2-arm_angle, 16, 12),
                     border_radius=3)

    # ── CABEZA ──
    head_w = 64
    head_h = 52
    head_x = cx - head_w//2
    head_y = torso_y - torso_h - head_h - 2 + bob
    pygame.draw.rect(surf, main_c, (head_x, head_y, head_w, head_h), border_radius=8)
    pygame.draw.rect(surf, lighter(main_c, 40), (head_x, head_y, head_w, head_h), 2, border_radius=8)
    # Visor alargado
    pygame.draw.rect(surf, BLACK, (head_x+6, head_y+14, head_w-12, 16), border_radius=5)
    # Ojos azules (2 grandes)
    pygame.draw.ellipse(surf, eye_c, (cx-20, head_y+15, 16, 12))
    pygame.draw.ellipse(surf, eye_c, (cx+4, head_y+15, 16, 12))
    pygame.draw.ellipse(surf, lighter(eye_c,80), (cx-18, head_y+16, 8, 6))
    pygame.draw.ellipse(surf, lighter(eye_c,80), (cx+6, head_y+16, 8, 6))
    # Detalle boca / rejilla
    for i in range(4):
        pygame.draw.line(surf, dark_c,
                         (head_x+8+i*12, head_y+34), (head_x+8+i*12, head_y+44), 2)
    # Antenas angulares estilo Transformers
    pygame.draw.line(surf, dark_c, (cx-20, head_y), (cx-30, head_y-18), 2)
    pygame.draw.line(surf, dark_c, (cx-30, head_y-18), (cx-22, head_y-26), 2)
    pygame.draw.line(surf, dark_c, (cx+20, head_y), (cx+30, head_y-18), 2)
    pygame.draw.line(surf, dark_c, (cx+30, head_y-18), (cx+22, head_y-26), 2)
    # Studs Lego en cabeza (detalle)
    for i in range(3):
        pygame.draw.ellipse(surf, lighter(main_c,20),
                            (head_x+8+i*22, head_y-6, 16, 10))

    _draw_droid_damage(surf, cx, head_y, torso_rect, hp_ratio, frame, main_c)


def _draw_droid_muerte(surf, cx, by, hp_ratio, frame):
    """
    Droide Muerte Negra - caótico multicolor con cráneo (foto 1).
    Bloques Lego de colores mezclados, capa negra, cabeza monstruosa.
    """
    bob = int(math.sin(frame * 0.07 + 1) * 3)
    W2 = 110
    H2 = 165

    # Colores caóticos de bloques Lego (como la foto)
    BRICK_COLORS = [RED, BLUE, GREEN, ORANGE, YELLOW, (200,0,200), TAN,
                    (0,200,200), (255,80,0), (0,100,255)]
    rng = random.Random(42)  # seed fija para que no parpadeen

    base_y = by + bob

    # ── PIES ──
    pygame.draw.rect(surf, BLACK, (cx-W2//2-5, base_y-20, 42, 20), border_radius=3)
    pygame.draw.rect(surf, BLACK, (cx+W2//2-37, base_y-20, 42, 20), border_radius=3)

    # ── PIERNAS (bloques de colores) ──
    leg_w = 28
    leg_h = 58
    # Pierna izquierda con bloques de colores
    _draw_block_leg(surf, cx-W2//2+2, base_y-20, leg_w, leg_h, rng, BRICK_COLORS)
    _draw_block_leg(surf, cx+W2//2-leg_w-2, base_y-20, leg_w, leg_h, rng, BRICK_COLORS)

    torso_y = base_y - 20 - leg_h

    # ── TORSO (bloques multicolor caóticos como foto 1) ──
    torso_w = W2
    torso_h = 80
    torso_top = torso_y - torso_h

    # Fondo negro del torso
    pygame.draw.rect(surf, BLACK,
                     (cx-torso_w//2, torso_top, torso_w, torso_h),
                     border_radius=6)
    # Bloques de colores encima del torso
    _draw_block_pattern(surf, cx-torso_w//2+2, torso_top+2,
                        torso_w-4, torso_h-4, rng, BRICK_COLORS)
    pygame.draw.rect(surf, BLACK,
                     (cx-torso_w//2, torso_top, torso_w, torso_h),
                     2, border_radius=6)

    # Emblema del pecho (símbolo rojo/naranja como en la foto)
    emb_x, emb_y = cx-18, torso_top+torso_h//2-15
    pygame.draw.rect(surf, RED, (emb_x, emb_y, 36, 30), border_radius=3)
    pygame.draw.rect(surf, ORANGE, (emb_x, emb_y, 36, 30), 2, border_radius=3)
    # Rayo
    pts = [(emb_x+18, emb_y+4), (emb_x+8, emb_y+15), (emb_x+17, emb_y+15),
           (emb_x+12, emb_y+26), (emb_x+26, emb_y+13), (emb_x+19, emb_y+13)]
    pygame.draw.polygon(surf, ORANGE, pts)

    # ── CAPA / TELA negra (característica de la foto 1) ──
    cape_y = torso_top
    cape_pts_l = [(cx-torso_w//2+5, cape_y+5),
                  (cx-torso_w//2-20, cape_y+60),
                  (cx-torso_w//2-15, torso_y+5),
                  (cx-torso_w//2+2, torso_y+5)]
    pygame.draw.polygon(surf, (10,10,20), cape_pts_l)
    cape_pts_r = [(cx+torso_w//2-5, cape_y+5),
                  (cx+torso_w//2+20, cape_y+60),
                  (cx+torso_w//2+15, torso_y+5),
                  (cx+torso_w//2-2, torso_y+5)]
    pygame.draw.polygon(surf, (10,10,20), cape_pts_r)

    # ── HOMBROS con bloques de colores ──
    sh_l = pygame.Rect(cx-torso_w//2-30, torso_top, 34, 44)
    sh_r = pygame.Rect(cx+torso_w//2-4, torso_top, 34, 44)
    for sh in [sh_l, sh_r]:
        pygame.draw.rect(surf, BLACK, sh, border_radius=5)
        _draw_block_pattern(surf, sh.x+2, sh.y+2, sh.w-4, sh.h-4, rng, BRICK_COLORS)
        pygame.draw.rect(surf, BLACK, sh, 2, border_radius=5)

    # ── BRAZOS ──
    arm_w = 18
    arm_h = 62
    arm_angle = int(math.sin(frame * 0.06) * 8)
    # Brazo izq - largo y negro con bloques
    arm_l = pygame.Rect(cx-torso_w//2-arm_w-12, torso_top+30+arm_angle, arm_w, arm_h)
    pygame.draw.rect(surf, BLACK, arm_l, border_radius=4)
    _draw_block_pattern(surf, arm_l.x+2, arm_l.y+2, arm_l.w-4, arm_l.h-4, rng, BRICK_COLORS, cell=10)
    pygame.draw.rect(surf, BLACK, arm_l, 1, border_radius=4)
    # Mano con garras
    pygame.draw.rect(surf, BLACK,
                     (arm_l.x-8, arm_l.bottom-12, arm_w+6, 14),
                     border_radius=3)
    for i in range(3):
        pygame.draw.rect(surf, DARK_GREY,
                         (arm_l.x-6+i*8, arm_l.bottom, 5, 8),
                         border_radius=2)
    # Brazo der
    arm_r = pygame.Rect(cx+torso_w//2+12, torso_top+30-arm_angle, arm_w, arm_h)
    pygame.draw.rect(surf, BLACK, arm_r, border_radius=4)
    _draw_block_pattern(surf, arm_r.x+2, arm_r.y+2, arm_r.w-4, arm_r.h-4, rng, BRICK_COLORS, cell=10)
    pygame.draw.rect(surf, BLACK, arm_r, 1, border_radius=4)
    pygame.draw.rect(surf, BLACK,
                     (arm_r.right-12, arm_r.bottom-12, arm_w+6, 14),
                     border_radius=3)
    for i in range(3):
        pygame.draw.rect(surf, DARK_GREY,
                         (arm_r.right-8+i*8, arm_r.bottom, 5, 8),
                         border_radius=2)

    # ── CABEZA MONSTRUOSA (como foto 1) ──
    head_w = 72
    head_h = 60
    head_x = cx - head_w//2
    head_y = torso_top - head_h - 4 + bob

    # Capucha exterior peluda / negra
    pygame.draw.ellipse(surf, (15,10,25),
                        (head_x-10, head_y-12, head_w+20, head_h+16))
    # Bloques de colores en hombros/capucha
    for i, bx in enumerate([cx-torso_w//2-5, cx+torso_w//2-25]):
        c = rng.choice(BRICK_COLORS)
        pygame.draw.rect(surf, c, (bx, head_y+4, 18, 12), border_radius=2)

    # Cráneo blanco
    pygame.draw.ellipse(surf, (215,215,220), (head_x, head_y, head_w, head_h))
    # Ojos verdes que brillan (como foto 1: lentes verdes)
    pygame.draw.ellipse(surf, (0,80,20), (cx-22, head_y+16, 18, 12))
    pygame.draw.ellipse(surf, (0,80,20), (cx+4, head_y+16, 18, 12))
    pygame.draw.ellipse(surf, (0,200,50), (cx-20, head_y+18, 14, 8))
    pygame.draw.ellipse(surf, (0,200,50), (cx+6, head_y+18, 14, 8))
    glow_alpha = int(abs(math.sin(frame*0.08))*80 + 100)
    eye_glow = pygame.Surface((20,14), pygame.SRCALPHA)
    eye_glow.fill((0,255,60, glow_alpha))
    surf.blit(eye_glow, (cx-21, head_y+17))
    surf.blit(eye_glow, (cx+3, head_y+17))
    # Nariz / mandíbula
    pygame.draw.ellipse(surf, (190,190,195), (cx-4, head_y+32, 8, 6))
    pygame.draw.line(surf, DARK_GREY,
                     (cx-10, head_y+42), (cx+10, head_y+42), 2)
    for i in range(5):
        pygame.draw.rect(surf, WHITE,
                         (cx-8+i*4, head_y+42, 3, 6))
    # Cuernos / protuberancias (foto 1 tiene algo en la cabeza)
    pygame.draw.polygon(surf, (190,190,195),
                        [(cx-12, head_y+2), (cx-20, head_y-12), (cx-4, head_y)])
    pygame.draw.polygon(surf, (190,190,195),
                        [(cx+12, head_y+2), (cx+20, head_y-12), (cx+4, head_y)])

    # Guadaña (elemento distintivo de La Muerte Negra)
    scythe_x = cx + torso_w//2 + arm_w + 20
    scythe_y = torso_top + 30
    swing = int(math.sin(frame * 0.05) * 8)
    pygame.draw.line(surf, (120,120,130),
                     (scythe_x, scythe_y + swing),
                     (scythe_x, scythe_y + 55 + swing), 3)
    pygame.draw.ellipse(surf, (100,100,110),
                        (scythe_x - 18, scythe_y + swing - 5, 22, 14))
    pygame.draw.ellipse(surf, (140,140,150),
                        (scythe_x - 16, scythe_y + swing - 3, 16, 8))

    _draw_droid_damage(surf, cx, head_y, pygame.Rect(cx-torso_w//2, torso_top, torso_w, torso_h),
                       hp_ratio, frame, BLACK)


def _draw_block_leg(surf, x, base_y, w, h, rng, colors):
    """Pierna con bloques Lego de colores."""
    pygame.draw.rect(surf, BLACK, (x, base_y-h, w, h), border_radius=3)
    # Bloques pequeños de colores encima
    _draw_block_pattern(surf, x+2, base_y-h+2, w-4, h-4, rng, colors, cell=12)
    pygame.draw.rect(surf, BLACK, (x, base_y-h, w, h), 1, border_radius=3)


def _draw_block_pattern(surf, x, y, w, h, rng, colors, cell=14):
    """Rellena un área con bloques de colores Lego aleatorios (seed fija)."""
    for row in range(0, h, cell):
        for col in range(0, w, cell):
            c = rng.choice(colors)
            bw = min(cell-1, w-col)
            bh = min(cell-1, h-row)
            if bw > 2 and bh > 2:
                pygame.draw.rect(surf, c, (x+col, y+row, bw, bh), border_radius=1)
                pygame.draw.rect(surf, lighter(c,30), (x+col, y+row, bw, bh), 1, border_radius=1)


def _draw_droid_damage(surf, cx, head_y, torso_rect, hp_ratio, frame, base_color):
    """Grietas y humo cuando el droide tiene poca vida."""
    if hp_ratio < 0.6:
        pygame.draw.line(surf, darker(base_color, 70),
                         (torso_rect.centerx - 10, torso_rect.top + 10),
                         (torso_rect.centerx + 20, torso_rect.top + 50), 2)
    if hp_ratio < 0.3:
        pygame.draw.line(surf, darker(base_color, 60),
                         (cx-15, head_y + 20), (cx+10, head_y + 45), 2)
        # Humo
        for i in range(3):
            smoke_x = cx + (i-1)*20
            smoke_y = head_y - 10 - int(math.sin(frame*0.1+i)*5)
            pygame.draw.circle(surf, (80,80,80), (smoke_x, smoke_y), 6+i*2)


# ──────────────────────────────────────────────────────
#  HUD
# ──────────────────────────────────────────────────────
def draw_hud(surf, pieces, max_pieces, gold_bricks, studs, hp, max_hp):
    hud_surf = pygame.Surface((W, 54), pygame.SRCALPHA)
    hud_surf.fill((10, 10, 30, 185))
    surf.blit(hud_surf, (0, 0))

    font_big = pygame.font.SysFont('Arial Black', 16, bold=True)
    font_sm  = pygame.font.SysFont('Arial', 12)

    draw_lego_piece(surf, 10, 18, BLUE, 14)
    surf.blit(font_big.render(f"{pieces}/{max_pieces}", True, WHITE), (30, 16))

    draw_stud(surf, 135, 23, 100)
    surf.blit(font_big.render(f"{studs:,}", True, GOLD), (147, 14))

    draw_gold_brick(surf, 256, 16)
    surf.blit(font_big.render(f"x{gold_bricks}", True, GOLD), (282, 14))

    for i in range(max_hp):
        hx = W - 28 - i*26
        color = RED if i < hp else DARK_GREY
        pygame.draw.rect(surf, color, (hx, 12, 20, 20), border_radius=4)
        if i < hp:
            pygame.draw.rect(surf, lighter(RED, 40), (hx, 12, 20, 20), 2)

    bar_x, bar_y = 10, 46
    bar_w = 190
    pygame.draw.rect(surf, DARK_GREY, (bar_x, bar_y, bar_w, 6), border_radius=3)
    fill = int(bar_w * min(pieces / max_pieces, 1.0))
    if fill > 0:
        pygame.draw.rect(surf, SABER_BLUE, (bar_x, bar_y, fill, 6), border_radius=3)
    pygame.draw.rect(surf, GREY, (bar_x, bar_y, bar_w, 6), 1, border_radius=3)
    surf.blit(font_sm.render("PIEZAS DROIDE", True, GREY), (bar_x + bar_w + 5, bar_y - 2))


def draw_lego_piece(surf, x, y, color, size=14):
    pygame.draw.rect(surf, color, (x, y, size, size//2 + 2), border_radius=2)
    pygame.draw.rect(surf, lighter(color, 40), (x, y, size, size//2 + 2), 1)
    for i in range(2):
        sx = x + 3 + i * 7
        pygame.draw.ellipse(surf, lighter(color, 30), (sx, y-4, 6, 5))
        pygame.draw.ellipse(surf, darker(color, 10), (sx, y-4, 6, 5), 1)
    pygame.draw.circle(surf, WHITE, (x+2, y+2), 2)


def draw_gold_brick(surf, x, y, pulse=0):
    glow = int(abs(math.sin(pulse * 0.05)) * 30)
    color = (min(255, GOLD[0]+glow), min(255, GOLD[1]+glow//2), 0)
    pygame.draw.rect(surf, color, (x, y, 20, 12), border_radius=2)
    pygame.draw.rect(surf, lighter(color, 60), (x, y, 20, 12), 1)
    for i in range(2):
        pygame.draw.ellipse(surf, lighter(color, 40), (x+3+i*9, y-4, 7, 6))
    if glow > 15:
        pygame.draw.line(surf, WHITE, (x+1, y+1), (x+5, y+5), 1)


def draw_stud(surf, x, y, value=10):
    colors = {10: GREY, 100: GOLD, 1000: BLUE, 10000: PURPLE}
    c = colors.get(value, GREY)
    pygame.draw.circle(surf, c, (x, y), 6)
    pygame.draw.circle(surf, lighter(c, 60), (x, y), 6, 1)
    pygame.draw.circle(surf, lighter(c, 80), (x-2, y-2), 2)
