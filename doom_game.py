import pygame
import math
import sys

pygame.init()

# =========================================================
# SETTINGS
# =========================================================

WIDTH = 1000
HEIGHT = 600

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

FOV = math.pi / 3
HALF_FOV = FOV / 2

NUM_RAYS = 400
DELTA_ANGLE = FOV / NUM_RAYS

MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)

FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Doom Style Game")

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================

SKY = (80, 130, 180)
FLOOR = (45, 45, 45)

WHITE = (255, 255, 255)
RED = (200, 40, 40)
GREEN = (40, 200, 60)
YELLOW = (255, 220, 50)
BLACK = (0, 0, 0)

# =========================================================
# MAP
# =========================================================

WORLD_MAP = [
    "1111111111111111",
    "1..............1",
    "1..............1",
    "1...111........1",
    "1..............1",
    "1......111.....1",
    "1..............1",
    "1....11........1",
    "1..............1",
    "1...........1111",
    "1..............1",
    "1111111111111111",
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)

TILE = 1

# =========================================================
# PLAYER
# =========================================================

player_x = 2.5
player_y = 2.5

player_angle = 0

PLAYER_SPEED = 0.06
ROTATION_SPEED = 0.04

# =========================================================
# ENEMIES
# =========================================================

enemies = [
    [7.5, 2.5],
    [11.5, 4.5],
    [6.5, 8.5],
    [12.5, 8.5]

]

enemy_alive = [True] * len(enemies)

# =========================================================
# CHECK WALL
# =========================================================

def is_wall(x, y):

    map_x = int(x)
    map_y = int(y)

    if map_x < 0 or map_x >= MAP_WIDTH:
        return True

    if map_y < 0 or map_y >= MAP_HEIGHT:
        return True

    return WORLD_MAP[map_y][map_x] == "1"


# =========================================================
# RAYCASTING
# =========================================================

def ray_casting():

    start_angle = player_angle - HALF_FOV

    wall_distances = []

    for ray in range(NUM_RAYS):

        ray_angle = start_angle + ray * DELTA_ANGLE

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        depth = 0

        while depth < MAX_DEPTH:

            depth += 0.02

            target_x = player_x + depth * cos_a
            target_y = player_y + depth * sin_a

            if is_wall(target_x, target_y):
                break

        # Fish-eye correction
        depth *= math.cos(player_angle - ray_angle)

        wall_distances.append(depth)

        # Wall height
        wall_height = int(SCREEN_DIST / (depth + 0.0001))

        # Don't draw outside screen
        if wall_height > HEIGHT:
            wall_height = HEIGHT

        # Distance-based shading
        shade = max(40, min(255, int(255 / (depth * 0.35))))

        color = (
            shade,
            shade,
            shade
        )

        x = int(ray * WIDTH / NUM_RAYS)

        pygame.draw.rect(
            screen,
            color,
            (
                x,
                HALF_HEIGHT - wall_height // 2,
                WIDTH // NUM_RAYS + 1,
                wall_height
            )
        )

    return wall_distances


# =========================================================
# DRAW ENEMIES
# =========================================================

def draw_enemies(wall_distances):

    visible_enemies = []

    for i, enemy in enumerate(enemies):

        if not enemy_alive[i]:
            continue

        dx = enemy[0] - player_x
        dy = enemy[1] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        angle = math.atan2(dy, dx)

        angle_diff = (angle - player_angle + math.pi) % (
            2 * math.pi
        ) - math.pi

        if abs(angle_diff) < HALF_FOV:

            screen_x = HALF_WIDTH + math.tan(angle_diff) * SCREEN_DIST

            size = int(400 / (distance + 0.1))

            if size < 10:
                continue

            visible_enemies.append(
                (
                    distance,
                    screen_x,
                    size,
                    i
                )
            )

    # Draw far enemies first
    visible_enemies.sort(reverse=True)

    for distance, screen_x, size, index in visible_enemies:

        x = int(screen_x)

        y = HALF_HEIGHT - size // 2

        if x < 0 or x >= WIDTH:
            continue

        ray_index = int(x / WIDTH * NUM_RAYS)

        if ray_index >= NUM_RAYS:
            ray_index = NUM_RAYS - 1

        if distance < wall_distances[ray_index]:

            pygame.draw.circle(
                screen,
                RED,
                (x, y + size // 2),
                size // 3
            )

            pygame.draw.rect(
                screen,
                RED,
                (
                    x - size // 4,
                    y + size // 2,
                    size // 2,
                    size // 2
                )
            )

            # Eyes
            pygame.draw.circle(
                screen,
                WHITE,
                (
                    x - size // 10,
                    y + size // 2
                ),
                max(2, size // 15)
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    x + size // 10,
                    y + size // 2
                ),
                max(2, size // 15)
            )


# =========================================================
# WEAPON
# =========================================================

def draw_weapon():

    # Gun body
    pygame.draw.rect(
        screen,
        (70, 70, 70),
        (
            HALF_WIDTH - 70,
            HEIGHT - 160,
            140,
            160
        )
    )

    # Gun barrel
    pygame.draw.rect(
        screen,
        (30, 30, 30),
        (
            HALF_WIDTH - 25,
            HEIGHT - 240,
            50,
            130
        )
    )

    # Handle
    pygame.draw.polygon(
        screen,
        (50, 50, 50),
        [
            (HALF_WIDTH - 50, HEIGHT - 40),
            (HALF_WIDTH + 50, HEIGHT - 40),
            (HALF_WIDTH + 30, HEIGHT),
            (HALF_WIDTH - 30, HEIGHT)
        ]
    )


# =========================================================
# SHOOT
# =========================================================

def shoot():

    best_enemy = None
    best_distance = 999

    for i, enemy in enumerate(enemies):

        if not enemy_alive[i]:
            continue

        dx = enemy[0] - player_x
        dy = enemy[1] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        angle = math.atan2(dy, dx)

        angle_diff = (angle - player_angle + math.pi) % (
            2 * math.pi
        ) - math.pi

        # Enemy must be near crosshair
        if abs(angle_diff) < 0.08:

            if distance < best_distance:

                # Check if wall is between player and enemy
                steps = int(distance * 20)

                blocked = False

                for step in range(steps):

                    t = step / steps

                    check_x = player_x + dx * t
                    check_y = player_y + dy * t

                    if is_wall(check_x, check_y):

                        blocked = True
                        break

                if not blocked:

                    best_enemy = i
                    best_distance = distance

    if best_enemy is not None:

        enemy_alive[best_enemy] = False


# =========================================================
# CROSSHAIR
# =========================================================

def draw_crosshair():

    pygame.draw.line(
        screen,
        WHITE,
        (
            HALF_WIDTH - 10,
            HALF_HEIGHT
        ),
        (
            HALF_WIDTH + 10,
            HALF_HEIGHT
        ),
        2
    )

    pygame.draw.line(
        screen,
        WHITE,
        (
            HALF_WIDTH,
            HALF_HEIGHT - 10
        ),
        (
            HALF_WIDTH,
            HALF_HEIGHT + 10
        ),
        2
    )


# =========================================================
# MINIMAP
# =========================================================

def draw_minimap():

    scale = 12

    for y in range(MAP_HEIGHT):

        for x in range(MAP_WIDTH):

            if WORLD_MAP[y][x] == "1":

                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        x * scale,
                        y * scale,
                        scale,
                        scale
                    )
                )

    # Player
    pygame.draw.circle(
        screen,
        YELLOW,
        (
            int(player_x * scale),
            int(player_y * scale)
        ),
        4
    )

    # Direction
    pygame.draw.line(
        screen,
        YELLOW,
        (
            int(player_x * scale),
            int(player_y * scale)
        ),
        (
            int(
                (player_x + math.cos(player_angle))
                * scale
            ),
            int(
                (player_y + math.sin(player_angle))
                * scale
            )
        ),
        2
    )


# =========================================================
# TEXT
# =========================================================

font = pygame.font.Font(None, 32)

def draw_text():

    alive = sum(enemy_alive)

    text = font.render(
        f"Enemies: {alive}",
        True,
        WHITE
    )

    screen.blit(
        text,
        (20, HEIGHT - 40)
    )


# =========================================================
# GAME LOOP
# =========================================================

running = True

while running:

    clock.tick(FPS)

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            if event.key == pygame.K_SPACE:

                shoot()

    # -----------------------------------------------------
    # KEYBOARD
    # -----------------------------------------------------

    keys = pygame.key.get_pressed()

    # Forward/backward
    move_x = 0
    move_y = 0

    if keys[pygame.K_w]:

        move_x += math.cos(player_angle) * PLAYER_SPEED
        move_y += math.sin(player_angle) * PLAYER_SPEED

    if keys[pygame.K_s]:

        move_x -= math.cos(player_angle) * PLAYER_SPEED
        move_y -= math.sin(player_angle) * PLAYER_SPEED

    # Strafe left
    if keys[pygame.K_a]:

        move_x += math.cos(player_angle - math.pi / 2) * PLAYER_SPEED
        move_y += math.sin(player_angle - math.pi / 2) * PLAYER_SPEED

    # Strafe right
    if keys[pygame.K_d]:

        move_x += math.cos(player_angle + math.pi / 2) * PLAYER_SPEED
        move_y += math.sin(player_angle + math.pi / 2) * PLAYER_SPEED

    # Collision movement
    new_x = player_x + move_x
    new_y = player_y + move_y

    if not is_wall(new_x, player_y):

        player_x = new_x

    if not is_wall(player_x, new_y):

        player_y = new_y

    # -----------------------------------------------------
    # ROTATION
    # -----------------------------------------------------

    if keys[pygame.K_LEFT]:

        player_angle -= ROTATION_SPEED

    if keys[pygame.K_RIGHT]:

        player_angle += ROTATION_SPEED

    # -----------------------------------------------------
    # DRAW SKY
    # -----------------------------------------------------

    screen.fill(SKY)

    # Floor
    pygame.draw.rect(
        screen,
        FLOOR,
        (
            0,
            HALF_HEIGHT,
            WIDTH,
            HALF_HEIGHT
        )
    )

    # -----------------------------------------------------
    # RAYCASTING
    # -----------------------------------------------------

    wall_distances = ray_casting()

    # -----------------------------------------------------
    # ENEMIES
    # -----------------------------------------------------

    draw_enemies(wall_distances)

    # -----------------------------------------------------
    # WEAPON
    # -----------------------------------------------------

    draw_weapon()

    # -----------------------------------------------------
    # CROSSHAIR
    # -----------------------------------------------------

    draw_crosshair()

    # -----------------------------------------------------
    # MINIMAP
    # -----------------------------------------------------

    draw_minimap()

    # -----------------------------------------------------
    # TEXT
    # -----------------------------------------------------

    draw_text()

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    pygame.display.flip()


pygame.quit()
sys.exit()