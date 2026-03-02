"""
Game state management for the Snake game.
Handles the snake's position, movement direction, food placement, game score and game over state and check collisions.
"""
from dataclasses import dataclass
from collections import deque
from direction import Direction
from random import randint

@dataclass
class GameState:
    snake_positions: deque
    direction: Direction
    food_position: tuple
    score: int
    game_over: bool
    grid_size: int = 8
    food_eaten: bool = False

    def __init__(self):
        self.snake_positions = deque([(4, 4), (4, 5), (4, 6)])  # Initial snake position
        self.direction = Direction.UP
        self.spawn_food()
        self.score = 0
        self.game_over = False

    def reset(self):
        self.__init__()
    
    def check_collision(self):
        head_x, head_y = self.snake_positions[0]
        # Check self collision
        if (head_x, head_y) in list(self.snake_positions)[1:]:
            self.game_over = True
        #TODO: Add wall collision if needed
    
    def spawn_food(self):
        while True:
            x = randint(0, self.grid_size - 1)
            y = randint(0, self.grid_size - 1)
            if (x, y) not in self.snake_positions:
                self.food_position = (x, y)
                break
    
    def check_food_collision(self):
        head_x, head_y = self.snake_positions[0]
        food_x, food_y = self.food_position
        return head_x == food_x and head_y == food_y
    
    def eat_food(self):
        self.score += 1
        self.food_eaten = True
        self.spawn_food()
    
    def move_snake(self, new_direction):
        if new_direction != Direction.NONE and self.is_valid_turn(new_direction):
            self.direction = new_direction
        head_x, head_y = self.snake_positions[0]
        if self.direction == Direction.UP:
            head_y -= 1
        elif self.direction == Direction.DOWN:
            head_y += 1
        elif self.direction == Direction.LEFT:
            head_x -= 1
        elif self.direction == Direction.RIGHT:
            head_x += 1
        else:
            pass  # This will not happen due to checks above

        head_x %= self.grid_size
        head_y %= self.grid_size
        new_head = (head_x, head_y)
        
        self.snake_positions.appendleft(new_head)
        
        if self.check_food_collision():
            self.eat_food()
        elif not self.food_eaten:
            self.snake_positions.pop()  # Remove tail if no food eaten
        else:
            self.food_eaten = False  # Reset food eaten flag
        
        self.check_collision()
    
    def is_valid_turn(self, new_direction):
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return new_direction != opposite_directions.get(self.direction, None)