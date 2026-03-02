"""
Handles input from the joystick for the Snake game.
Initializes the MCP3008 ADC using software SPI on custom GPIO pins.
Wiring required:
    MCP3008:
        VDD/VREF  -> Pin 1  (3.3V)
        AGND/DGND -> Pin 6 (Ground)
        CLK       -> Pin 29 (GPIO 23)
        DOUT      -> Pin 31 (GPIO 24)
        DIN       -> Pin 33 (GPIO 25)
        CS        -> Pin 35 (GPIO 12)
    Joystick:
        GND       -> Pin 6 (Ground)
        +5V       -> Pin 1 (3.3V)
        VRX       -> MCP3008 CH0
        VRY       -> MCP3008 CH1
        SW        -> Pin 37 (GPIO 26)    
All wirings are different from Pironman's usual pins to avoid conflicts.
All wirings are different from LED matrix's pins to avoid conflicts.    
"""
from gpiozero import MCP3008, Button
from direction import Direction
from config import MCP_CLK, MCP_MOSI, MCP_MISO, MCP_CS, BTN_PIN, INPUT_POLL_INTERVAL
import time

class InputHandler:
    def __init__(self):
        self.joystick_x = MCP3008(channel=0, clock_pin=MCP_CLK, mosi_pin=MCP_MOSI, miso_pin=MCP_MISO, select_pin=MCP_CS)
        self.joystick_y = MCP3008(channel=1, clock_pin=MCP_CLK, mosi_pin=MCP_MOSI, miso_pin=MCP_MISO, select_pin=MCP_CS)
        self.button = Button(BTN_PIN)
    
    def get_direction(self):
        x = self.joystick_x.value
        y = self.joystick_y.value

        threshold_radius = 0.1
        mid = 0.5

        dx = x - mid
        dy = y - mid
        distance_squared = (dx*dx + dy*dy)

        if distance_squared < threshold_radius * threshold_radius:
            return Direction.NONE
            
        if abs(dx) > abs(dy):
                return Direction.LEFT if dx < 0 else Direction.RIGHT
        else:
                return Direction.UP if dy < 0 else Direction.DOWN
    
    def poll_for_direction_input(self, timeout):
        last_direction = Direction.NONE
        elapsed_time = 0.0
        while elapsed_time < timeout:
            direction = self.get_direction()
            if direction != Direction.NONE:
                last_direction = direction
            time.sleep(INPUT_POLL_INTERVAL)
            elapsed_time += INPUT_POLL_INTERVAL
        return last_direction
    
    def has_joystick_moved(self):
        direction = self.get_direction()
        return direction != Direction.NONE

    def is_button_pressed(self):
        return self.button.is_pressed
