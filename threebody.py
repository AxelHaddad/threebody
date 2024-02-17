#! /usr/bin/env python3
from math import ceil
from random import randint

import pygame
from pygame import Vector2, color, gfxdraw
from pygame.color import Color

SCREEN_SIZE: tuple[int, int] = (1280, 720)
MIN_DISTANCE: float = 50  # To Avoid crazy accelerations when bodies are too close
G: float = 900
NUMBER_OF_STARS: int = 3
BACKGROUND_COLOR = "black"


def random_color() -> Color:
    return Color(randint(0, 255), randint(0, 255), randint(0, 255))


def random_position() -> Vector2:
    x_margin = ceil(SCREEN_SIZE[0] / 10)
    x = randint(x_margin, SCREEN_SIZE[0] - x_margin)
    y_margin = ceil(SCREEN_SIZE[1] / 10)
    y = randint(y_margin, SCREEN_SIZE[1] - y_margin)
    return Vector2(x, y)


def random_mass() -> float:
    mass = randint(1000, 4000)
    normalized_mass = mass * 4 / NUMBER_OF_STARS
    return normalized_mass


def size_from_mass(mass: float) -> float:
    """Just linear here, for more representation"""
    return max(mass / 50, 3)


MASSES: list[float] = [random_mass() for _ in range(NUMBER_OF_STARS)]
SIZES: list[float] = [size_from_mass(mass) for mass in MASSES]


INITIAL_POSITIONS: list[Vector2] = [random_position() for _ in range(NUMBER_OF_STARS)]
INITIAL_VELOCITIES: list[Vector2] = [Vector2(0, 0) for _ in range(NUMBER_OF_STARS)]
COLORS: list[color.Color] = [random_color() for _ in range(NUMBER_OF_STARS)]


def compute_accelerations(
    positions: list[Vector2], masses: list[float]
) -> list[Vector2]:
    accelerations = [Vector2(0, 0) for _ in range(NUMBER_OF_STARS)]
    for i in range(NUMBER_OF_STARS):
        # we will compute the acceleration vector for each body
        # and add it to the accelerations list
        for j in range(NUMBER_OF_STARS):
            if i == j:
                continue
            # first we compute the unit direction vector from i to j
            vector_between_the_two = positions[j] - positions[i]
            distance = vector_between_the_two.length()
            if distance <= 1:
                continue
            unit_direction = vector_between_the_two.normalize()
            # then we compute the acceleration of i from the  gravity of and j
            accelerations[i] += (
                masses[j] * G / max(distance, MIN_DISTANCE) ** 2
            ) * unit_direction
    return accelerations


def compute_velocities(
    velocities: list[Vector2], accelerations: list[Vector2], dt: float
) -> list[Vector2]:
    return [
        velocity + acceleration * dt
        for (velocity, acceleration) in zip(velocities, accelerations)
    ]


def compute_positions(
    positions: list[Vector2], velocities: list[Vector2], dt_in_s: float
) -> list[Vector2]:
    return [
        position + velocity * dt_in_s
        for (position, velocity) in zip(positions, velocities)
    ]


def draw_circle(surface, color, position: Vector2, radius):
    x, y = round(position.x), round(position.y)
    int_radius = round(radius)
    if int_radius > 5:
        # no need to use anti-aliasing for small circles
        gfxdraw.aacircle(surface, x, y, int_radius, color)
    gfxdraw.filled_circle(surface, x, y, int_radius, color)


def draw_bodies(positions: list[Vector2]):
    for color, position, size in zip(COLORS, positions, SIZES):
        draw_circle(screen, color, position, size)


if __name__ == "__main__":
    # Example file showing a basic pygame "game loop"
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True
    dt_in_s = 0

    positions: list[Vector2] = INITIAL_POSITIONS
    velocities: list[Vector2] = INITIAL_VELOCITIES

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
