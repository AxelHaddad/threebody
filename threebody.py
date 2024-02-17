#! /usr/bin/env python3
import argparse
from math import ceil
from random import randint

import pygame
from pygame import Surface, Vector2, gfxdraw
from pygame.color import Color

SCREEN_SIZE: tuple[int, int] = (1280, 720)
MIN_DISTANCE: float = 50  # To Avoid crazy accelerations when bodies are too close
MIN_DISTANCE_SQUARED: float = MIN_DISTANCE**2
GRAVITATIONAL_COEFFICIENT: float = 900
DEFAULT_NUMBER_OF_STARS: int = 3
BACKGROUND_COLOR = "black"


def random_color() -> Color:
    return Color(randint(0, 255), randint(0, 255), randint(0, 255))


def random_position() -> Vector2:
    x_margin = ceil(SCREEN_SIZE[0] / 10)
    x = randint(x_margin, SCREEN_SIZE[0] - x_margin)
    y_margin = ceil(SCREEN_SIZE[1] / 10)
    y = randint(y_margin, SCREEN_SIZE[1] - y_margin)
    return Vector2(x, y)


def random_mass(number_of_stars: int) -> float:
    mass = randint(1000, 4000)
    normalized_mass = mass * 4 / number_of_stars
    return normalized_mass


def size_from_mass(mass: float) -> float:
    """Just linear here, for more representation"""
    return max(mass / 50, 3)


GravitationFactor = tuple[list[float], ...]
"""Contains the gravitation factor between each pair of stars.
I.e. G/(distance**2) where G is the gravitational constant.

Only store it for i < j, as the factor is the same for i and j.
Aim at being mutated.
"""


class State:
    """Assumes that after init or after update, the state is consistent."""

    number_of_stars: int
    masses: tuple[float, ...]
    sizes: tuple[float, ...]
    positions: tuple[Vector2, ...]
    velocities: tuple[Vector2, ...]
    colors: tuple[Color, ...]
    gravitation_factor: GravitationFactor
    accelerations: tuple[Vector2, ...]

    def __init__(self, number_of_stars: int):
        self.number_of_stars = number_of_stars
        self.masses = tuple(
            random_mass(number_of_stars) for _ in range(number_of_stars)
        )
        self.sizes = tuple(size_from_mass(mass) for mass in self.masses)
        self.positions = tuple(random_position() for _ in range(number_of_stars))
        self.velocities = tuple(Vector2(0, 0) for _ in range(number_of_stars))
        self.colors = tuple(random_color() for _ in range(number_of_stars))
        self.gravitation_factor = tuple(
            [0 for _ in range(number_of_stars)] for _ in range(number_of_stars)
        )
        self.accelerations = tuple(Vector2(0, 0) for _ in range(number_of_stars))
        self._update_gravitation_factor()
        self._update_acceleration()

    def _update_gravitation_factor(self):
        for i in range(self.number_of_stars):
            for j in range(i + 1, self.number_of_stars):
                distance_squared = self.positions[i].distance_squared_to(
                    self.positions[j]
                )
                self.gravitation_factor[i][j] = GRAVITATIONAL_COEFFICIENT / max(
                    distance_squared, MIN_DISTANCE_SQUARED
                )

    def _update_acceleration(self):
        for i in range(self.number_of_stars):
            self.accelerations[i].update(0, 0)
            for j in range(self.number_of_stars):
                if i == j:
                    continue
                # first we compute the unit direction vector from i to j
                vector = self.positions[j] - self.positions[i]
                distance = vector.length()
                if distance <= 1:
                    continue
                vector.normalize_ip()
                vector.scale_to_length(
                    self.masses[j] * self.gravitation_factor[min(i, j)][max(i, j)]
                )
                self.accelerations[i].x += vector.x
                self.accelerations[i].y += vector.y

    def _update_velocities(self, dt_in_s: float):
        for i in range(self.number_of_stars):
            self.velocities[i].x += self.accelerations[i].x * dt_in_s
            self.velocities[i].y += self.accelerations[i].y * dt_in_s

    def _update_positions(self, dt_in_s: float):
        for i in range(self.number_of_stars):
            self.positions[i].x += self.velocities[i].x * dt_in_s
            self.positions[i].y += self.velocities[i].y * dt_in_s

    def update(self, dt_in_s: float):
        self._update_velocities(dt_in_s)
        self._update_positions(dt_in_s)
        self._update_gravitation_factor()
        self._update_acceleration()


def draw_circle_aa(screen: Surface, color: Color, position: Vector2, radius: float):
    x, y = round(position.x), round(position.y)
    int_radius = round(radius)
    gfxdraw.aacircle(screen, x, y, int_radius, color)
    gfxdraw.filled_circle(screen, x, y, int_radius, color)


def draw_circle_no_aa(screen: Surface, color: Color, position: Vector2, radius: float):
    x, y = round(position.x), round(position.y)
    int_radius = round(radius)
    gfxdraw.filled_circle(screen, x, y, int_radius, color)


def draw_bodies_aa(state: State, screen: Surface):
    for color, position, size in zip(state.colors, state.positions, state.sizes):
        draw_circle_aa(screen, color, position, size)


def draw_bodies_no_aa(state: State, screen: Surface):
    for color, position, size in zip(state.colors, state.positions, state.sizes):
        draw_circle_aa(screen, color, position, size)


def run_simulation(number_of_stars: int):
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True
    dt_in_s = 0

    state = State(number_of_stars)

    draw_bodies = draw_bodies_aa
    if state.number_of_stars > 100:
        draw_bodies = draw_bodies_no_aa

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        state.update(dt_in_s)

        screen.fill(BACKGROUND_COLOR)
        draw_bodies(state, screen)
        pygame.display.flip()

        dt_in_s = clock.tick(60) / 1000  # limits FPS to 60

    pygame.quit()


if __name__ == "__main__":
    # use arparse to get the number of stars from the command line
    parser = argparse.ArgumentParser(
        prog="threebody", description="Simulate the movement of stars in a 2D space"
    )
    # add an optional argument but without -n or something
    parser.add_argument(
        "number_of_stars",
        nargs="?",
        type=int,
        help="The number of stars to simulate",
        default=DEFAULT_NUMBER_OF_STARS,
    )
    args = parser.parse_args()

    run_simulation(args.number_of_stars)
