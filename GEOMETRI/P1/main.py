import pygame

# =====================================
# INISIALISASI
# =====================================
pygame.init()

WIDTH = 1400
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Representasi Parametrik Parabola")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)
font_small = pygame.font.SysFont("Arial", 14)

# =====================================
# WARNA
# =====================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)

BLUE = (50, 100, 255)
RED = (255, 50, 50)
GREEN = (0, 180, 0)

# =====================================
# PARAMETER PARABOLA
# =====================================
xp = 250
yp = HEIGHT // 2

a = 1.5
scale = 3

t_min = -15
t_max = 15

t = t_min
dt = 0.1

play = True
points = []

running = True

while running:

    screen.fill(WHITE)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                play = not play

            elif event.key == pygame.K_RIGHT:
                t = min(t + dt, t_max)

            elif event.key == pygame.K_LEFT:
                t = max(t - dt, t_min)

            elif event.key == pygame.K_HOME:
                t = t_min
                points.clear()

            elif event.key == pygame.K_END:
                t = t_max

            elif event.key == pygame.K_r:
                t = t_min
                points.clear()

            elif event.key == pygame.K_UP:
                dt += 0.05

            elif event.key == pygame.K_DOWN:
                dt = max(0.05, dt - 0.05)

    # GRID
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    # SUMBU
    pygame.draw.line(screen, BLACK, (0, yp), (WIDTH, yp), 3)
    pygame.draw.line(screen, BLACK, (xp, 0), (xp, HEIGHT), 3)

    # PARAMETRIK
    x_math = a * (t ** 2)
    y_math = 2 * a * t

    x_screen = xp + (x_math * scale)
    y_screen = yp - (y_math * scale)

    if play:
        points.append((x_screen, y_screen))

    # LINTASAN
    for p in points:
        pygame.draw.circle(screen, BLUE, (int(p[0]), int(p[1])), 2)

    # VERTEX
    pygame.draw.circle(screen, GREEN, (xp, yp), 8)

    # GARIS BANTU
    pygame.draw.line(screen, GRAY, (xp, int(y_screen)), (int(x_screen), int(y_screen)), 1)
    pygame.draw.line(screen, GRAY, (int(x_screen), yp), (int(x_screen), int(y_screen)), 1)

    # TITIK
    pygame.draw.circle(screen, RED, (int(x_screen), int(y_screen)), 10)

    # KOORDINAT
    koordinat = f"({x_math:.2f}, {y_math:.2f})"
    screen.blit(font.render(koordinat, True, RED),
                (int(x_screen)+15, int(y_screen)-15))

    # INFO
    screen.blit(font.render("REPRESENTASI PARAMETRIK PARABOLA", True, BLACK), (500, 20))
    screen.blit(font.render("x = xp + a*t²", True, BLACK), (20, 20))
    screen.blit(font.render("y = yp + 2*a*t", True, BLACK), (20, 50))

    status = "PLAY" if play else "PAUSE"

    screen.blit(font.render(f"Status : {status}", True, RED), (20, 100))
    screen.blit(font.render(f"t = {t:.2f}", True, BLACK), (20, 130))
    screen.blit(font.render(f"dt = {dt:.2f}", True, BLACK), (20, 160))

    if play:
        t += dt

        if t > t_max:
            t = t_max
            play = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()