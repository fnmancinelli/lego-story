# LEGO Story - Entry point
import pygame
import sys
from settings import W, H, FPS, TITLE
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(TITLE)

    # Ícono amarillo (stud Lego)
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, (255, 205, 0), (16, 16), 14)
    pygame.draw.circle(icon, (200, 160, 0), (16, 16), 14, 2)
    pygame.display.set_icon(icon)

    game = Game(screen)
    clock = pygame.time.Clock()

    while True:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        game.handle_events(events)
        game.update(1 / FPS)
        game.draw()
        pygame.display.flip()


if __name__ == '__main__':
    main()
