"""
Configuration for constant values used in the snake game.
"""

# Joystick MCP3008 Software SPI Pins
MCP_CLK = 23    # Pin 29 - Clock
MCP_MOSI = 25   # Pin 33 - Data to MCP3008 (DIN)
MCP_MISO = 24   # Pin 31 - Data from MCP3008 (DOUT)
MCP_CS = 12     # Pin 35 - Chip Select
# Joystick button pin
BTN_PIN = 26    # Pin 37


# LED Matrix Software SPI Pins
LED_CLK = 16    # Pin 36 - Clock
LED_DIN = 20    # Pin 38 - Data In
LED_CS = 21     # Pin 40 - Chip Select

# Game settings
GAME_SPEED = 0.3  # Delay between game updates in seconds
BOARD_WIDTH = 8
BOARD_HEIGHT = 8
INITIAL_SNAKE_LENGTH = 3
INPUT_POLL_INTERVAL = 0.05  # Interval to poll joystick input in seconds
DEFAULT_ANIMATION_INTERVAL = 0.5  # Interval between animation frames in seconds
SCROLL_SPEED = 0.08  # Seconds per pixel for scrolling score