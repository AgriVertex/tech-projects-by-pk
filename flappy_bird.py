import pygame
import random
import sys

pygame.init()

# ---------------- SCREEN ----------------
WIDTH = 500
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BLUE = (80, 180, 255)
GREEN = (0, 180, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)

# ---------------- FONT ----------------
font = pygame.font.Font(None, 50)

# ---------------- BIRD ----------------
bird_x = 100
bird_y = 300
bird_radius = 18

bird_velocity = 0
gravity = 0.5
jump = -9

# ---------------- PIPES ----------------
pipe_width = 70
pipe_gap = 180
pipe_speed = 4


class Pipe:
    def __init__(self, x):
        gap_y = random.randint(150, 500)

        self.top_pipe = pygame.Rect(
            x,
            0,
            pipe_width,
            gap_y - pipe_gap // 2
        )

        self.bottom_pipe = pygame.Rect(
            x,
            gap_y + pipe_gap // 2,
            pipe_width,
            HEIGHT - (gap_y + pipe_gap // 2)
        )

        self.passed = False


# ---------------- CREATE PIPES ----------------
def create_pipes():
    return [
        Pipe(WIDTH),
        Pipe(WIDTH + 280)
    ]


pipes = create_pipes()

# ---------------- GAME VARIABLES ----------------
score = 0
game_over = False
running = True


# ---------------- RESET GAME ----------------
def reset_game():
    global bird_y
    global bird_velocity
    global pipes
    global score
    global game_over

    bird_y = 300
    bird_velocity = 0

    pipes = create_pipes()

    score = 0
    game_over = False


# ---------------- GAME LOOP ----------------
while running:

    clock.tick(60)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                if game_over:
                    reset_game()
                else:
                    bird_velocity = jump

    # ---------------- GAME ----------------
    if not game_over:

        # Bird movement
        bird_velocity += gravity
        bird_y += bird_velocity

        # Bird rectangle
        bird = pygame.Rect(
            bird_x - bird_radius,
            int(bird_y) - bird_radius,
            bird_radius * 2,
            bird_radius * 2
        )

        # Move pipes
        for pipe in pipes:
            pipe.top_pipe.x -= pipe_speed
            pipe.bottom_pipe.x -= pipe_speed

        # Remove old pipe and create new one
        if pipes[0].top_pipe.right < 0:
            pipes.pop(0)
            pipes.append(Pipe(WIDTH))

        # Collision with pipes
        for pipe in pipes:

            if bird.colliderect(pipe.top_pipe):
                game_over = True

            if bird.colliderect(pipe.bottom_pipe):
                game_over = True

        # Collision with ground or ceiling
        if bird.top <= 0 or bird.bottom >= HEIGHT:
            game_over = True

        # Score
        for pipe in pipes:

            if not pipe.passed and pipe.top_pipe.right < bird_x:

                pipe.passed = True
                score += 1

    # ---------------- DRAW BACKGROUND ----------------
    screen.fill(BLUE)

    # ---------------- DRAW PIPES ----------------
    for pipe in pipes:

        pygame.draw.rect(
            screen,
            GREEN,
            pipe.top_pipe
        )

        pygame.draw.rect(
            screen,
            GREEN,
            pipe.bottom_pipe
        )

    # ---------------- DRAW BIRD ----------------
    pygame.draw.circle(
        screen,
        YELLOW,
        (bird_x, int(bird_y)),
        bird_radius
    )

    # ---------------- DRAW SCORE ----------------
    score_text = font.render(
        str(score),
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (
            WIDTH // 2 - score_text.get_width() // 2,
            30
        )
    )

    # ---------------- GAME OVER ----------------
    if game_over:

        game_over_text = font.render(
            "GAME OVER",
            True,
            BLACK
        )

        restart_text = font.render(
            "Press SPACE",
            True,
            BLACK
        )

        screen.blit(
            game_over_text,
            (
                WIDTH // 2 -
                game_over_text.get_width() // 2,
                300
            )
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 -
                restart_text.get_width() // 2,
                360
            )
        )

    # ---------------- UPDATE SCREEN ----------------
    pygame.display.update()


# ---------------- QUIT ----------------
pygame.quit()
sys.exit()