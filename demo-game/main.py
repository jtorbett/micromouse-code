import math
import os
import random
import time
from collections import deque
from typing import Tuple, Deque

import pygame
import pygame.font
import serial

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

    lines = build_lines()

    font = pygame.font.Font(None, 64)
    victory = False
    failure = False
    lsd = False
    mouse_view_mode = False
    non_render_count = 0

    left_response = 0
    right_response = 0

    controller = SerialPortController()

    start_time = time.time() + 5

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
            lines = build_lines()
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
                    controller = SerialPortController()
                else:
                    controller = None
                lsd = True
        else:
            lsd = False

        speed_1, speed_2 = 0, 0
        if controller is not None:
            speed_1, speed_2 = controller.update(left_response, right_response)
            speeds.append((min(1., max(-1., speed_1)), min(1., max(-1., speed_2))))

        # while len(speeds) > 30:
        #     speeds.popleft()
        #
        # speed_1 = sum(speed[0] for speed in speeds) / 30
        # speed_2 = sum(speed[1] for speed in speeds) / 30

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

        negative_intersect = 1000000
        positive_intersect = 1000000
        left_hidden = False
        right_hidden = False
        for start, end, hidden in lines:
            start.rotate_ip_rad(-angle_change)
            start.y += robot_velocity
            end.rotate_ip_rad(-angle_change)
            end.y += robot_velocity

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

        if player_pos.y < -72300:
            victory = True
        if negative_intersect < (10 if left_hidden else 20) or positive_intersect < (10 if right_hidden else 20):
            failure = True

        left_response = 0
        right_response = 0
        if negative_intersect < 200 and not left_hidden:
            left_response = (200 - negative_intersect) / 180
        if positive_intersect < 200 and not right_hidden:
            right_response = (200 - positive_intersect) / 180

        render_dt += dt
        non_render_count += 1

        should_render = render_dt == 0 or render_dt >= 1/60

        if should_render:
            render(dots, font, left_response, lines, mouse, mouse_draw_pos, right_response, score, screen, speed_1, speed_2, victory, failure, start_time, mouse_view_mode)

            render_dt = 0
            non_render_count = 0

        dt = clock.tick(1000) / 1000

    pygame.quit()


def render(dots, font, left_response, lines, mouse, mouse_draw_pos, right_response, score, screen, speed_1, speed_2, victory, failure, start_time, mouse_view_mode):
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("#1C1E26")
    for dot in dots:
        pygame.draw.circle(screen, "grey", dot + mouse_draw_pos, radius=1)
    screen.blit(mouse, mouse.get_rect(center=mouse_draw_pos).topleft)
    for start, end, hidden in lines:
        if mouse_view_mode:
            ms = pygame.Vector2(start.x, start.y + abs(start.x/2))
            me = pygame.Vector2(end.x, end.y + abs(end.x/2))
            pygame.draw.line(screen, "black" if hidden else "red", ms + mouse_draw_pos, me + mouse_draw_pos, width=8)
        else:
            pygame.draw.line(screen, "black" if hidden else "red", start + mouse_draw_pos, end + mouse_draw_pos, width=8)

    if left_response:
        if mouse_view_mode:
            dot = pygame.Vector2(-20 - (1-left_response) * 180, 0)
        else:
            dot = pygame.Vector2(-20 - (1-left_response) * 180, (-20 - (1-left_response) * 180) / 2)
        pygame.draw.circle(screen, "green", dot + mouse_draw_pos, radius=4)
    if right_response:
        if mouse_view_mode:
            dot = pygame.Vector2(20 + (1-right_response) * 180, 0)
        else:
            dot = pygame.Vector2(20 + (1-right_response) * 180, (-20 - (1-right_response) * 180) / 2)
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

def build_lines():
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

    return lines


if __name__ == '__main__':
    main()
