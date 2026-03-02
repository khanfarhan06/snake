"""
Sprite definitions for 8x8 LED matrix animations.

Each sprite is a 64-bit hex value representing an 8x8 bitmap.
Hex format: 0xROW76ROW5ROW4ROW3ROW2ROW1ROW0
- Each byte is one row, MSB = leftmost pixel

Usage:
    from sprites import Sprite, SPRITES
    pattern = SPRITES[Sprite.FACE_RIGHT]
"""

from enum import Enum, auto


class Sprite(Enum):
    FACE_RIGHT = auto()
    FACE_LEFT = auto()
    FACE_WINK = auto()
    HEART_FULL = auto()
    HEART_HALF = auto()
    HEART_QUARTER = auto()
    HEART_DOT = auto()
    CROSS_FULL = auto()
    CROSS_HALF = auto()
    CROSS_QUARTER = auto()
    CROSS_DOT = auto()
    EMPTY = auto()
    FULL = auto()  # All LEDs on


# Raw hex values for each sprite (1=OFF, 0=ON format)
_SPRITE_HEX = {
    Sprite.FACE_RIGHT: 0x003c4200006c6c00,
    Sprite.FACE_LEFT:  0x003c420000363600,
    Sprite.FACE_WINK:  0x003c4200006c6000,
    Sprite.HEART_FULL: 0x081c3e7f7f7f3600,
    Sprite.HEART_HALF: 0x00081c3e3e140000,
    Sprite.HEART_QUARTER: 0x0000081c14000000,
    Sprite.HEART_DOT: 0x0000000800000000,
    Sprite.CROSS_FULL: 0x8142241818244281,
    Sprite.CROSS_HALF: 0x0042241818244200,
    Sprite.CROSS_QUARTER: 0x0000241818240000,
    Sprite.CROSS_DOT: 0x0000001818000000,
    Sprite.EMPTY: 0x0000000000000000,
    Sprite.FULL: 0xffffffffffffffff,  # All LEDs on
}


def _hex_to_pattern(hex_value: int) -> list[list[int]]:
    """
    Convert a 64-bit hex value to an 8x8 pattern list.
    """
    pattern = []
    for row in range(8):
        byte = (hex_value >> (row * 8)) & 0xFF
        row_pixels = []
        for col in range(8):
            bit = (byte >> (col)) & 1
            row_pixels.append(bit)
        pattern.append(row_pixels) 
    return pattern


# Pre-computed patterns at module load time
# Access via: SPRITES[Sprite.FACE_RIGHT]
SPRITES: dict[Sprite, list[list[int]]] = {
    sprite: _hex_to_pattern(hex_val) 
    for sprite, hex_val in _SPRITE_HEX.items()
}
