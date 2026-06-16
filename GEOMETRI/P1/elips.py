import pygame
import math

# =====================================
# INISIALISASI
# =====================================
pygame.init()

WIDTH = 1400
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "Representasi Parametrik Elips"
)

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
# PARAMETER ELIPS
# =====================================
xp = WIDTH // 2
yp = HEIGHT // 2

# sumbu mayor dan minor
a = 120
b = 70

scale = 3

t_min = 0
t_max = 2 * math.pi

t = t_min

dt = 0.5

play = True

points = []

running = True

# =====================================
# LOOP UTAMA
# =====================================
while running:

    screen.fill(WHITE)

    # =====================================
    # EVENT
    # =====================================
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
                dt += 0.01

            elif event.key == pygame.K_DOWN:
                dt = max(0.005, dt - 0.01)

    # =====================================
    # GRID
    # =====================================
    for x_grid in range(0, WIDTH, 50):

        pygame.draw.line(
            screen,
            GRAY,
            (x_grid, 0),
            (x_grid, HEIGHT)
        )

    for y_grid in range(0, HEIGHT, 50):

        pygame.draw.line(
            screen,
            GRAY,
            (0, y_grid),
            (WIDTH, y_grid)
        )

    # =====================================
    # SUMBU
    # =====================================
    pygame.draw.line(
        screen,
        BLACK,
        (0, yp),
        (WIDTH, yp),
        3
    )

    pygame.draw.line(
        screen,
        BLACK,
        (xp, 0),
        (xp, HEIGHT),
        3
    )

    # =====================================
    # LABEL KOORDINAT
    # =====================================
    for x_grid in range(0, WIDTH, 50):

        nilai_x = int((x_grid - xp) / scale)

        label = font_small.render(
            str(nilai_x),
            True,
            BLACK
        )

        screen.blit(
            label,
            (x_grid + 2, yp + 5)
        )

    for y_grid in range(0, HEIGHT, 50):

        nilai_y = int((yp - y_grid) / scale)

        label = font_small.render(
            str(nilai_y),
            True,
            BLACK
        )

        screen.blit(
            label,
            (xp + 5, y_grid)
        )

    screen.blit(
        font.render("X", True, BLACK),
        (WIDTH - 30, yp + 10)
    )

    screen.blit(
        font.render("Y", True, BLACK),
        (xp + 10, 10)
    )

    # =====================================
    # PARAMETRIK ELIPS
    # =====================================
    x_math = a * math.cos(t)
    y_math = b * math.sin(t)

    x_screen = xp + (x_math * scale)
    y_screen = yp - (y_math * scale)

    if play:
        points.append((x_screen, y_screen))

    # =====================================
    # LINTASAN
    # =====================================
    for p in points:

        pygame.draw.circle(
            screen,
            BLUE,
            (int(p[0]), int(p[1])),
            2
        )

    # =====================================
    # PUSAT ELIPS
    # =====================================
    pygame.draw.circle(
        screen,
        GREEN,
        (xp, yp),
        8
    )

    screen.blit(
        font.render(
            "Pusat",
            True,
            GREEN
        ),
        (xp + 10, yp + 10)
    )

    # =====================================
    # GARIS BANTU
    # =====================================
    pygame.draw.line(
        screen,
        GRAY,
        (xp, int(y_screen)),
        (int(x_screen), int(y_screen)),
        1
    )

    pygame.draw.line(
        screen,
        GRAY,
        (int(x_screen), yp),
        (int(x_screen), int(y_screen)),
        1
    )

    # =====================================
    # TITIK BERGERAK
    # =====================================
    pygame.draw.circle(
        screen,
        RED,
        (int(x_screen), int(y_screen)),
        10
    )

    # =====================================
    # LABEL KOORDINAT
    # =====================================
    koordinat = f"({x_math:.2f}, {y_math:.2f})"

    screen.blit(
        font.render(
            koordinat,
            True,
            RED
        ),
        (int(x_screen) + 15,
         int(y_screen) - 15)
    )

    # =====================================
    # JUDUL
    # =====================================
    screen.blit(
        font.render(
            "REPRESENTASI PARAMETRIK ELIPS",
            True,
            BLACK
        ),
        (520, 20)
    )

    # =====================================
    # RUMUS
    # =====================================
    screen.blit(
        font.render(
            "x = xp + a*cos(t)",
            True,
            BLACK
        ),
        (20, 30)
    )

    screen.blit(
        font.render(
            "y = yp + b*sin(t)",
            True,
            BLACK
        ),
        (20, 60)
    )

    # =====================================
    # STATUS
    # =====================================
    status = "PLAY" if play else "PAUSE"

    screen.blit(
        font.render(
            f"Status : {status}",
            True,
            RED
        ),
        (20, 120)
    )

    screen.blit(
        font.render(
            f"t = {t:.2f}",
            True,
            BLACK
        ),
        (20, 160)
    )

    screen.blit(
        font.render(
            f"dt = {dt:.3f}",
            True,
            BLACK
        ),
        (20, 200)
    )

    screen.blit(
        font.render(
            f"a = {a}",
            True,
            BLACK
        ),
        (20, 240)
    )

    screen.blit(
        font.render(
            f"b = {b}",
            True,
            BLACK
        ),
        (20, 280)
    )

    # =====================================
    # PETUNJUK
    # =====================================
    petunjuk = [
        "SPACE : Play/Pause",
        "RIGHT : Maju",
        "LEFT : Mundur",
        "HOME : Awal",
        "END : Akhir",
        "R : Reset",
        "UP : Percepat",
        "DOWN : Perlambat"
    ]

    for i, teks in enumerate(petunjuk):

        screen.blit(
            font.render(
                teks,
                True,
                BLACK
            ),
            (1120, 30 + i * 35)
        )

    # =====================================
    # UPDATE PARAMETER
    # =====================================
    if play:

        t += dt

        if t > t_max:

            t = t_max
            play = False

    pygame.display.update()

    clock.tick(60)

pygame.quit()