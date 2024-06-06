import math
import os
import random
import time
from collections import deque
from typing import Tuple, Deque

import pygame
import pygame.font
import serial

from maze import ObstacleCourse, Maze

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

max_speed = 500


class DemoController:
    def __init__(self):
        self._last_left_signal = 0
        self._last_right_signal = 0
        self._last_ratio = 0
        self._p = 1.6
        self._i = 0.02
        self._iratio = 0
        self._d = 120
        self._change = 0

    def update(self, left_signal, right_signal) -> Tuple[float, float]:
        if not left_signal:
            if right_signal:
                left_signal = (self._last_left_signal + self._last_right_signal) - right_signal
            else:
                left_signal = 0.9
                right_signal = 0.9
                self._last_left_signal *= 0.99
                self._last_right_signal *= 0.99
                self._iratio = 0
        elif not right_signal:
            right_signal = (self._last_left_signal + self._last_right_signal) - left_signal
        else:
            self._last_left_signal = left_signal
            self._last_right_signal = right_signal

        ratio = right_signal - left_signal
        self._iratio += ratio
        self._change = ratio - self._last_ratio

        top_speed = min(1, (2 - self._last_left_signal - self._last_right_signal) * 1.6)
        if abs(ratio) > 0.1:
            top_speed *= 0.1 / abs(ratio)
        if abs(self._change) > 0.05:
            top_speed *= 0.05 / abs(self._change)

        correction = ((self._p * ratio) + (self._i * self._iratio) + (self._d * self._change)) * (1 + top_speed) / 2

        if correction < 0:
            speed_1 = top_speed
            speed_2 = max(0, top_speed + correction)
        elif correction > 0:
            speed_1 = max(0, top_speed - correction)
            speed_2 = top_speed
        else:
            speed_1 = speed_2 = top_speed

        self._last_ratio = ratio
        return speed_1, speed_2

    def reset(self):
        self._last_left_signal = 0
        self._last_right_signal = 0
        self._last_ratio = 0
        self._iratio = 0
        self._change = 0


class SerialPortController:
    def __init__(self):
        self.serial_port = serial.Serial("/dev/tty.usbmodem11303", baudrate=115200)
        self.rx_data: bytearray = bytearray()

    def update(self, left_signal, right_signal) -> Tuple[float, float]:
        speed_1 = 0
        speed_2 = 0

        if self.serial_port is not None:
            tx_data = bytes([
                max(0, min(255, math.floor(left_signal * 254) + 1)),
                max(0, min(255, math.floor(right_signal * 254) + 1)),
                0,
                ])
            self.serial_port.write(tx_data)
            self.rx_data.extend(self.serial_port.read_all())
            while len(self.rx_data) >= 3:
                inputs, separator, self.rx_data = self.rx_data.partition(b'\0')
                if len(inputs) == 2:
                    speed_1 = (inputs[0] - 128) / 127
                    speed_2 = (inputs[1] - 128) / 127

        return speed_1, speed_2

    def reset(self):
        pass

def clamp(_input):
    return max(min(_input, 1), 0)


def score_eq(distance, time_taken) -> float:
    speed = distance / time_taken if time_taken else 0
    return math.floor(distance / 7.23 * speed / 500)


def main():
    pygame.init()

    screen = pygame.display.set_mode((1600, 900), vsync=1)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    render_dt = 0
    mouse_draw_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() * 3 / 4)
    player_pos = pygame.Vector2(0, 0)
    player_angle = 0
    player_heading = pygame.Vector2(1, 0)

    speeds: Deque[Tuple[float, float]] = deque()
    score = 0

    axle_radius = 25
    mouse = pygame.image.load(os.path.join(BASE_PATH, "mouse.png"))

    dots = [
        pygame.Vector2(random.randint(-1000, 1000), random.randint(-1000, 1000))
        for _i in range(400)
    ]

    #maze = Maze(os.path.join(BASE_PATH, "2011uk-techfest.maze"))
    maze = ObstacleCourse()

    font = pygame.font.Font(None, 64)
    victory = False
    failure = False
    lsd = False
    mouse_view_mode = False
    non_render_count = 0

    left_response = 0
    right_response = 0

    controller = DemoController()

    start_time = time.time() + 5

    maze.reset()

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            speed_1 = speed_2 = 0
            player_pos = pygame.Vector2(0, 0)
            player_angle = 0
            player_heading = pygame.Vector2(1, 0)
            maze.reset()
            controller.reset()
            failure = False
            victory = False
            start_time = time.time() + 5

        if keys[pygame.K_ESCAPE]:
            running = False

        if keys[pygame.K_v]:
            if not lsd:
                mouse_view_mode = not mouse_view_mode
                lsd = True
        elif keys[pygame.K_p]:
            if not lsd:
                if controller is None:
                    controller = DemoController()
                else:
                    controller = None
                lsd = True
        else:
            lsd = False

        speed_1, speed_2 = 0, 0
        if controller is not None:
            speed_1, speed_2 = map(clamp, controller.update(left_response, right_response))

        if isinstance(controller, DemoController):
            speeds.append((speed_1, speed_2))
            while len(speeds) > 30:
                speeds.popleft()

            speed_1 = sum(speed[0] for speed in speeds) / 30
            speed_2 = sum(speed[1] for speed in speeds) / 30

        if time.time() < start_time:
            speed_1 = 0
            speed_2 = 0
            score = 0
        elif victory or failure:
            speed_1 = 0
            speed_2 = 0
        else:
            score = score_eq(-player_pos.y, time.time() - start_time)

        v1 = max_speed * dt * math.copysign(math.sqrt(abs(speed_1)), speed_1)
        v2 = max_speed * dt * math.copysign(math.sqrt(abs(speed_2)), speed_2)

        angle_change = (v1 - v2) / (2 * axle_radius)
        robot_velocity = (v1 + v2) / 2
        player_angle += angle_change
        player_heading.from_polar((1, math.degrees(player_angle) - 90))
        player_pos += player_heading * robot_velocity

        for dot in dots:
            dot.rotate_ip_rad(-angle_change)
            dot.y += robot_velocity
            if dot.x < -1000:
                dot.x += 2000
            elif dot.x > 1000:
                dot.x -= 2000
            if dot.y < -1000:
                dot.y += 2000
            elif dot.y > 1000:
                dot.y -= 2000

        maze.update(angle_change, robot_velocity)

        left_distance, right_distance = maze.sensor_distances()

        if player_pos.y < -72300:
            victory = True
        if left_distance < 10 or right_distance < 10:
            failure = True

        left_response = 0
        right_response = 0
        if left_distance < 500:
            left_response = (500 - left_distance) / 480
        if right_distance < 500:
            right_response = (500 - right_distance) / 480

        render_dt += dt
        non_render_count += 1

        should_render = render_dt == 0 or render_dt >= 1/60

        if should_render:
            render(dots, font, left_response, maze, mouse, mouse_draw_pos, right_response, score, screen, speed_1, speed_2, victory, failure, start_time, mouse_view_mode)

            render_dt = 0
            non_render_count = 0

        dt = clock.tick(1000) / 1000

    pygame.quit()


def render(dots, font, left_response, maze, mouse, mouse_draw_pos, right_response, score, screen, speed_1, speed_2, victory, failure, start_time, mouse_view_mode):
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("#1C1E26")
    for dot in dots:
        pygame.draw.circle(screen, "grey", dot + mouse_draw_pos, radius=1)
    screen.blit(mouse, mouse.get_rect(center=mouse_draw_pos).topleft)

    maze.render(screen, mouse_draw_pos, mouse_view_mode)

    if left_response:
        if mouse_view_mode:
            dot = pygame.Vector2(-20 - (1-left_response) * 480, 0)
        else:
            dot = pygame.Vector2(-20 - (1-left_response) * 480, (-20 - (1-left_response) * 480) / 2)
        pygame.draw.circle(screen, "green", dot + mouse_draw_pos, radius=4)
    if right_response:
        if mouse_view_mode:
            dot = pygame.Vector2(20 + (1-right_response) * 480, 0)
        else:
            dot = pygame.Vector2(20 + (1-right_response) * 480, (-20 - (1-right_response) * 480) / 2)
        pygame.draw.circle(screen, "green", dot + mouse_draw_pos, radius=4)

    pygame.draw.rect(screen, "white", pygame.Rect(10, 10, 20, 500 + 1), width=1)
    pygame.draw.rect(screen, "red", pygame.Rect(11, 511 - (left_response * 500), 18, (left_response * 500)))
    pygame.draw.rect(screen, "white", pygame.Rect(32, 10, 20, 500 + 1), width=1)
    pygame.draw.rect(screen, "green", pygame.Rect(33, 10 + 250 + 1 - max(0, speed_1 * 250), 18, abs(speed_1 * 250)))
    pygame.draw.rect(screen, "white", pygame.Rect(54, 10, 20, 500 + 1), width=1)
    pygame.draw.rect(screen, "green", pygame.Rect(55, 10 + 250 + 1 - max(0, speed_2 * 250), 18, abs(speed_2 * 250)))
    pygame.draw.rect(screen, "white", pygame.Rect(76, 10, 20, 500 + 1), width=1)
    pygame.draw.rect(screen, "red", pygame.Rect(77, 511 - (right_response * 500), 18, (right_response * 500)))

    if time.time() < start_time:
        countdown = math.ceil(start_time - time.time())
        text = font.render(f"{countdown}", True, "white")
        textpos = text.get_rect(centerx=screen.get_width()/2, centery=screen.get_height()/2)
        screen.blit(text, textpos)
    text = font.render(f"{score}", True, "green" if victory else "red" if failure else "white")
    textpos = text.get_rect(right=screen.get_width() - 10, y=10)
    screen.blit(text, textpos)
    pygame.display.flip()


if __name__ == '__main__':
    main()
