import math
from abc import ABC, abstractmethod
from copy import copy

import pygame

class BaseMaze(ABC):
    def __init__(self):
        self._lines = []

    def update(self, d_theta, d_pos):
        for start, end, hidden in self._lines:
            start.rotate_ip_rad(-d_theta)
            start.y += d_pos
            end.rotate_ip_rad(-d_theta)
            end.y += d_pos

    def sensor_distances(self):
        negative_intersect = 1000000
        positive_intersect = 1000000
        left_hidden = False
        right_hidden = False
        for start, end, hidden in self._lines:
            ms = pygame.Vector2(start.x, start.y + abs(start.x/2))
            me = pygame.Vector2(end.x, end.y + abs(end.x/2))

            if me.y < 0 <= ms.y or ms.y < 0 <= me.y:
                y_ratio = (-ms.y) / (me.y - ms.y)
                x_intersect = (me.x - ms.x) * y_ratio + ms.x
                if x_intersect < 0:
                    x_intersect *= -1
                    if x_intersect < negative_intersect:
                        negative_intersect = x_intersect
                        left_hidden = hidden
                else:
                    if x_intersect < positive_intersect:
                        positive_intersect = x_intersect
                        right_hidden = hidden

        if left_hidden and negative_intersect >= 10:
            negative_intersect = 1000000

        if right_hidden and positive_intersect >= 10:
            positive_intersect = 1000000

        return negative_intersect, positive_intersect

    def render(self, screen, offset, mouse_view_mode):
        for start, end, hidden in self._lines:
            if mouse_view_mode:
                ms = pygame.Vector2(start.x, start.y + abs(start.x/2))
                me = pygame.Vector2(end.x, end.y + abs(end.x/2))
                pygame.draw.line(screen, "black" if hidden else "red", ms + offset, me + offset, width=8)
            else:
                pygame.draw.line(screen, "black" if hidden else "red", start + offset, end + offset, width=8)

    @abstractmethod
    def reset(self):
        pass


class ObstacleCourse(BaseMaze):
    def reset(self):
        width = 120
        last_center = pygame.Vector2(0, 100)
        last_1 = pygame.Vector2(-width, 100)
        last_2 = pygame.Vector2(width, 100)
        step_size = 50
        lines = [(pygame.Vector2(-width, 100), pygame.Vector2(width, 100), True)]
        for i in range(1500):
            x = i * math.sin(i ** (1.1 + 0.2 * math.sin(i / 50)) / 100) * math.sin((i ** 1.25) / 77)
            center = pygame.Vector2(x, -i * step_size)
            _distance, angle = (center - last_center).as_polar()
            center = last_center + pygame.Vector2.from_polar((step_size, angle))
            new1 = pygame.Vector2.from_polar((width, angle - 90)) + center
            new2 = pygame.Vector2.from_polar((width, angle + 90)) + center

            left_hidden = False
            right_hidden = False
            if i >= 1497:
                left_hidden = True
                right_hidden = True

            if 501 == i:
                left_hidden = True
                right_hidden = True

            if i > 999:
                left_hidden = (i % 89) < 4
                right_hidden = (i % 67) < 4

            lines.append((last_1.copy(), new1, left_hidden))
            lines.append((last_2.copy(), new2, right_hidden))
            last_1 = new1
            last_2 = new2
            last_center = center
            if 420 < i <= 460:
                width -= 2  # Shrink by 80
            if 500 == i:
                width += 400  # Grow by 200
            if 530 < i <= 550:
                width -= 19  # Shrink by 380
            if 600 < i <= 1497:
                width += 0.6 * math.sin(i / 20)  # Pulsate

            if 1497 < i <= 1500:
                width = 0  # Completely disappear
        self._lines = lines


def dup(n, times):
    return [copy(n) for i in range(times)]


class Maze(BaseMaze):
    def __init__(self, filename):
        self._filename = filename
        self._cell_size = 100
        super().__init__()

    def to_world(self, x, y):
        return pygame.Vector2(x * self._cell_size, y * -self._cell_size)

    def reset(self):
        with open(self._filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        half_cell_size = self._cell_size / 2

        walls = []
        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                if (col % 2) == (row % 2):
                    continue
                if char == '|':
                    cell_x = col // 2
                    cell_y = 15 - (row // 2)
                    cell_center = self.to_world(cell_x, cell_y)
                    p1 = cell_center + pygame.Vector2(-half_cell_size, -half_cell_size)
                    p2 = cell_center + pygame.Vector2(-half_cell_size, half_cell_size)
                    walls.append((p1, p2, False))
                if char == '-':
                    cell_x = col // 2
                    cell_y = 15 - (row // 2)
                    cell_center = self.to_world(cell_x, cell_y)
                    p1 = cell_center + pygame.Vector2(-half_cell_size, -half_cell_size)
                    p2 = cell_center + pygame.Vector2(half_cell_size, -half_cell_size)
                    walls.append((p1, p2, False))

        self._lines = walls
