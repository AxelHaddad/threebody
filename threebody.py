#! /usr/bin/env python3
import pygame

SCREEN_SIZE: tuple[int, int] = (1280, 720)
MIN_DISTANCE: float = 50  # To Avoid crazy accelerations when bodies are too close
G: float = 1000
SIZES: list[int] = [40, 20, 10]
MASSES: list[float] = [2000, 1000, 3500]
BACKGROUND_COLOR = "black"
INITIAL_POSITIONS: list[pygame.Vector2] = [
    pygame.Vector2(300, 300),
    pygame.Vector2(500, 300),
    pygame.Vector2(400, 500),
]
INITIAL_VELOCITIES: list[pygame.Vector2] = [
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0),
    pygame.Vector2(0, 0),
]
COLORS: list[str] = ["red", "green", "blue"]
STAR_COUNT = len(SIZES)

assert (
    STAR_COUNT
    == len(MASSES)
    == len(INITIAL_POSITIONS)
    == len(INITIAL_VELOCITIES)
    == len(COLORS)
), "All lists must be the same length"


def compute_accelerations(
    positions: list[pygame.Vector2], masses: list[float]
) -> list[pygame.Vector2]:
    accelerations = [pygame.Vector2(0, 0) for _ in range(STAR_COUNT)]
    for i in range(STAR_COUNT):
        # we will compute the acceleration vector for each body
        # and add it to the accelerations list
        for j in range(STAR_COUNT):
            if i == j:
                continue
            # first we compute the unit direction vector from i to j
            vector_between_the_two = positions[j] - positions[i]
            distance = vector_between_the_two.length()
            unit_direction = vector_between_the_two.normalize()
            # then we compute the acceleration of i from the  gravity of and j
            accelerations[i] += (
                masses[j] * G / max(distance, MIN_DISTANCE) ** 2
            ) * unit_direction
    return accelerations


def compute_velocities(
    velocities: list[pygame.Vector2], accelerations: list[pygame.Vector2], dt: float
) -> list[pygame.Vector2]:
    return [
        velocity + acceleration * dt
        for (velocity, acceleration) in zip(velocities, accelerations)
    ]


def compute_positions(
    positions: list[pygame.Vector2], velocities: list[pygame.Vector2], dt_in_s: float
) -> list[pygame.Vector2]:
    return [
        position + velocity * dt_in_s
        for (position, velocity) in zip(positions, velocities)
    ]


def draw_bodies(positions: list[pygame.Vector2]):
    for color, position, size in zip(COLORS, positions, SIZES):
        pygame.draw.circle(screen, color, position, size)


if __name__ == "__main__":
    # Example file showing a basic pygame "game loop"
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True
    dt_in_s = 0

    positions: list[pygame.Vector2] = INITIAL_POSITIONS
    velocities: list[pygame.Vector2] = INITIAL_VELOCITIES

    BACKGROUND_COLOR = "black"

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        accelerations = compute_accelerations(positions, MASSES)
        velocities = compute_velocities(velocities, accelerations, dt_in_s)
        positions = compute_positions(positions, velocities, dt_in_s)

        screen.fill(BACKGROUND_COLOR)
        draw_bodies(positions)
        pygame.display.flip()

        dt_in_s = clock.tick(60) / 1000  # limits FPS to 60

    pygame.quit()
