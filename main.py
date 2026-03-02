"""
Handles the main game loop for the Snake game.
Sets up the game state, input handler, and renderer.
"""
from input_handler import InputHandler
from renderer import Renderer
from game_state import GameState
from config import GAME_SPEED

def game_loop():
    print("Starting the Snake game...")
    print("Press joystick button to start!")
    
    input_handler = InputHandler()
    renderer = Renderer()
    
    while True:
        # Loop intro animation until button is pressed
        renderer.play_intro_animation_loop(should_stop=input_handler.is_button_pressed)
        
        game_state = _play_game(input_handler, renderer)
        
        renderer.play_game_over_animation(game_state, game_state.score, should_stop=input_handler.is_button_pressed)
        print(f"Game over! Score: {game_state.score}")


def _play_game(input_handler: InputHandler, renderer: Renderer) -> GameState:
    """Play one round of the game, return final game state."""
    print("Game starting...")
    game_state = GameState()

    renderer.draw_game_frame(game_state)
    print(f"Score: {game_state.score}")

    while not game_state.game_over:
        direction = input_handler.poll_for_direction_input(timeout=GAME_SPEED)
        
        # move_snake handles: direction validation, movement, food eating, collision
        game_state.move_snake(direction)
        
        renderer.draw_game_frame(game_state)
    
    return game_state


if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        print("\nExiting...")
