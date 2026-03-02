"""
Handles rendering of the Snake game using 8x8 LED matrix.
Initializes the 8x8 LED matrix display using software SPI on custom GPIO pins.
Wiring required:
    LED Matrix:
        VCC       -> Pin 2  (3.3V)
        GND       -> Pin 6 (Ground)
        DIN       -> Pin 38 (GPIO 20)
        CLK       -> Pin 36 (GPIO 16)
        CS        -> Pin 40 (GPIO 21)
All wirings are different from Pironman's usual pins to avoid conflicts.
All wirings are different from MCP3008's pins + Joystick button to avoid conflicts.

NOTE: This code works with the gpiozero library's bitbang SPI implementation.
It does not use hardware SPI to avoid conflicts with other peripherals.
Implementation does not use LEDMatrix class from gpiozero due to lack of software SPI support.
"""

from config import LED_CLK, LED_DIN, LED_CS, INPUT_POLL_INTERVAL, DEFAULT_ANIMATION_INTERVAL, SCROLL_SPEED, BOARD_WIDTH, BOARD_HEIGHT
from luma.core.interface.serial import bitbang
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, textsize
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT
from sprites import Sprite, SPRITES
import time

class Renderer:
    def __init__(self):
        serial = bitbang(SCLK=LED_CLK, SDA=LED_DIN, CE=LED_CS)
        device = max7219(serial, rotate=2)
        self.matrix = device

    def draw_game_frame(self, game_state):
        with canvas(self.matrix) as draw:
            # Draw snake
            for pos in game_state.snake_positions:
                x, y = pos
                draw.point((x, y), fill="white")
            # Draw food
            food_x, food_y = game_state.food_position
            draw.point((food_x, food_y), fill="white")
    
    def _draw_pattern(self, pattern):
        """Draw an 8x8 pattern to the matrix."""
        with canvas(self.matrix) as draw:
            for y, row in enumerate(pattern):
                for x, pixel in enumerate(row):
                    if pixel:
                        draw.point((x, y), fill="white")
    
    def play_intro_animation_loop(self, should_stop) -> None:
        """Play intro animation loop until should_stop() returns True."""
        while True:
            should_start_game = self._play_face_animation(should_stop)
            if should_start_game:
                break
        # Spiral fade out: full → empty from outside in
        self._play_spiral_fade_out(speed=0.015)
        time.sleep(0.2)
    
    def play_game_over_animation(self, game_state, score: int, should_stop):
        """
        Play game over sequence:
        1. Blank → final game frame → blank → spiral fill in
        2. Scrolling score until button pressed
        """
        self._play_game_over_sequence(game_state)
        self._show_scrolling_score(score, should_stop)
        self.clear()
        time.sleep(0.2)
    
    def _play_face_animation(self, should_stop):
        face_animations = [
            SPRITES[Sprite.FACE_RIGHT],
            SPRITES[Sprite.FACE_LEFT],
            SPRITES[Sprite.FACE_RIGHT],
            SPRITES[Sprite.FACE_WINK],
            SPRITES[Sprite.FACE_RIGHT],
        ]
        for face_animation in face_animations:
            self._draw_pattern(face_animation)
            if self._wait_or_stop(DEFAULT_ANIMATION_INTERVAL, should_stop):
                return True
        return False
    
    def _play_spiral_fade_out(self, speed: float = 0.02):
        """
        Spiral fade out animation: full screen → LEDs turn off from outside → inside.
        """
        # Start with all LEDs on
        lit_pixels = set(SPIRAL_OUTSIDE_IN)  # All 64 pixels
        
        for coord in SPIRAL_OUTSIDE_IN:
            lit_pixels.discard(coord)  # Turn off this pixel
            self._draw_pixels(lit_pixels)
            time.sleep(speed)
        
        # End with blank screen
        self.clear()
    
    def _play_spiral_fade_in(self, speed: float = 0.02):
        """
        Spiral fade in animation: empty screen → LEDs turn on from inside → outside.
        """
        lit_pixels = set()
        
        for coord in SPIRAL_INSIDE_OUT:
            lit_pixels.add(coord)  # Turn on this pixel
            self._draw_pixels(lit_pixels)
            time.sleep(speed)
    
    def _draw_pixels(self, pixels: set[tuple[int, int]]):
        """Draw only the specified pixel coordinates."""
        with canvas(self.matrix) as draw:
            for x, y in pixels:
                draw.point((x, y), fill="white")
    
    def _play_game_over_sequence(self, game_state):
        """
        Game over sequence:
        1. Blank screen
        2. Show final game frame (snake + food at death)
        3. Blank screen
        4. Spiral fade in from inside out
        """
        speed = DEFAULT_ANIMATION_INTERVAL / 2
        
        # 1. Blank screen
        self.clear()
        time.sleep(speed)
        
        # 2. Show final game frame
        self.draw_game_frame(game_state)
        time.sleep(speed * 2)
        
        # 3. Blank screen
        self.clear()
        time.sleep(speed)
        
        # 4. Spiral fade in
        self._play_spiral_fade_in(speed=0.015)
        time.sleep(speed)
    
    def _play_heart_animation(self):
        speed = DEFAULT_ANIMATION_INTERVAL/2
        # Show expanding heart animation
        hearts = [
            SPRITES[Sprite.HEART_DOT],
            SPRITES[Sprite.HEART_QUARTER],
            SPRITES[Sprite.HEART_HALF],
            SPRITES[Sprite.HEART_FULL],
        ]
        for heart in hearts:
            self._draw_pattern(heart)
            time.sleep(speed)
        # Show contracting heart animation
        for heart in reversed(hearts):
            self._draw_pattern(heart)
            time.sleep(speed)

    def _play_cross_animation(self):
        speed = DEFAULT_ANIMATION_INTERVAL/2
        self._draw_pattern(SPRITES[Sprite.EMPTY])
        time.sleep(speed)
        self._draw_pattern(SPRITES[Sprite.FULL])
        time.sleep(speed)

        crosses = [
            SPRITES[Sprite.CROSS_DOT],
            SPRITES[Sprite.CROSS_QUARTER],
            SPRITES[Sprite.CROSS_HALF],
            SPRITES[Sprite.CROSS_FULL],
        ]
        for cross in crosses:
            self._draw_pattern(cross)
            time.sleep(speed)
        for i in range(3):
            self._draw_pattern(SPRITES[Sprite.EMPTY])
            time.sleep(speed)
            self._draw_pattern(SPRITES[Sprite.CROSS_FULL])
            time.sleep(speed)
    
    def _show_scrolling_score(self, score: int, should_stop):
        """Show infinite scrolling score until should_stop() returns True."""
        # For smooth scrolling we use virtual viewport.
        # Draw the score message twice for seamless looping:
        # [   Score: 100    Score: 100  ]
        #    ↑_____________↑
        #    message_width (one full cycle)
        
        message = f"{score}  "  # Extra space for gap
        font = proportional(CP437_FONT)
        message_width, _ = textsize(message, font)
        
        virtual = viewport(self.matrix, width=200, height=8)
        with canvas(virtual) as draw:
            # First copy
            text(draw, (0, 1), message, fill="white", font=font)
            # Second copy for seamless wrap
            text(draw, (message_width, 1), message, fill="white", font=font)
        
        offset = 0
        scroll_speed = SCROLL_SPEED  # Seconds per pixel
        while True:
            virtual.set_position((offset, 0))
            if self._wait_or_stop(scroll_speed, should_stop):
                break
            offset += 1
            if offset >= message_width:
                offset = 0
    
    def _wait_or_stop(self, duration: float, should_stop) -> bool:
        """
        Wait for duration while checking should_stop callback.
        Returns True if should_stop() returned True (stop requested).
        """
        elapsed = 0.0
        poll_interval = INPUT_POLL_INTERVAL  # Check every 50ms
        while elapsed < duration:
            if should_stop():
                return True
            time.sleep(poll_interval)
            elapsed += poll_interval
        return False
    
    def clear(self):
        self.matrix.clear()


def _generate_spiral_coords_outside_in(width: int, height: int) -> list[tuple[int, int]]:
    """
    Generate coordinates in spiral order from outside edge towards center.
    Goes clockwise starting from top-left corner.
    """
    coords = []
    top, bottom, left, right = 0, height - 1, 0, width - 1
    
    while top <= bottom and left <= right:
        # Top row: left to right
        for x in range(left, right + 1):
            coords.append((x, top))
        top += 1
        
        # Right column: top to bottom
        for y in range(top, bottom + 1):
            coords.append((right, y))
        right -= 1
        
        # Bottom row: right to left
        if top <= bottom:
            for x in range(right, left - 1, -1):
                coords.append((x, bottom))
            bottom -= 1
        
        # Left column: bottom to top
        if left <= right:
            for y in range(bottom, top - 1, -1):
                coords.append((left, y))
            left += 1
    
    return coords


def _generate_spiral_coords_inside_out(width: int, height: int) -> list[tuple[int, int]]:
    """
    Generate coordinates in spiral order from center towards outside edge.
    Simply reverses the outside-in spiral.
    """
    return list(reversed(_generate_spiral_coords_outside_in(width, height)))


# Pre-compute spiral coordinates at module load
SPIRAL_OUTSIDE_IN = _generate_spiral_coords_outside_in(BOARD_WIDTH, BOARD_HEIGHT)
SPIRAL_INSIDE_OUT = _generate_spiral_coords_inside_out(BOARD_WIDTH, BOARD_HEIGHT)

