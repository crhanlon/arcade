#!/usr/bin/env python
#
# Connor's Tron
# A simple tron game
#

import random
import time
import pygame

POSSIBLE_DIRECTIONS = {"RIGHT", "LEFT", "UP", "DOWN"}
PLAYER_OPTIONS = ['A', 'B', 'C', 'D']
BLOCK_SIZE = 5
GRID_WIDTH = 100
GRID_HEIGHT = 100


class Tron:
    def __init__(self, num_players=2):
        self.state = "PLAYING"
        self.grid = Grid()
        self.players = []
        for n in range(num_players):
            self.add_player(PLAYER_OPTIONS[n])

    def add_player(self, player_id):
        if len(self.players) >= 2:
            raise Exception("Maximum 2 players")
        if player_id == "A":
            initial_position = (0, 0)
            initial_direction = "RIGHT"
        elif player_id == "B":
            initial_position = (GRID_HEIGHT-1, GRID_WIDTH-1)
            initial_direction = "LEFT"
        else:
            raise Exception("Invalid player id {}".format(player_id))
        num_attempts = 0
        successful_addition = False
        while not successful_addition and num_attempts < 100:
            if self.grid.grid[initial_position[0]][initial_position[1]] == '-':
                successful_addition = True
            else:
                initial_position = self.grid.get_random_position()

        if successful_addition:
            self.grid.grid[initial_position[0]][initial_position[1]] = player_id
            self.players.append(Player(player_id, initial_position, initial_direction))
            return True
        else:
            return False

    def turn(self, screen):
        successful_turns = {'A': True, 'B': True}
        updated_rects = []
        for p in self.players:
            current_position = p.get_position()
            player_new_position = p.get_next_position(self.grid.grid)
            new_position_status = self.grid.grid[player_new_position[0]][player_new_position[1]]
            if new_position_status == '-':
                successful_turns[p.id] = True
                self.grid.grid[player_new_position[0]][player_new_position[1]] = p.id
                p.set_position(player_new_position)
                # Update screen
                if p.id == "A":
                    col = (0, 0, 255)
                else:
                    col = (255, 0, 0)
                py_rect = get_rect(player_new_position)
                updated_r = pygame.draw.rect(screen, col, py_rect, 0)
                updated_rects.append(updated_r)
            else:
                # Did they hit each other on the same turn?
                if new_position_status.isupper():
                    successful_turns[new_position_status] = False
                successful_turns[p.id] = False
                self.grid.grid[player_new_position[0]][player_new_position[1]] = 'X'
                py_rect = get_rect(player_new_position)
                updated_r = pygame.draw.rect(screen, (0, 0, 0), py_rect, 0)
                updated_rects.append(updated_r)

            self.grid.grid[current_position[0]][current_position[1]] = p.id.lower()

        if successful_turns["A"] and not successful_turns["B"]:
            self.state = "Player A Won!"
        elif successful_turns["B"] and not successful_turns["A"]:
            self.state = "Player B Won!"
        elif not successful_turns["A"] and not successful_turns["B"]:
            self.state = "IT'S A TIE!"

        return updated_rects


class Grid:
    def __init__(self, grid_size=(GRID_HEIGHT, GRID_WIDTH)):
        self.grid = []
        for i in range(grid_size[0]):
            row = []
            for j in range(grid_size[1]):
                row.append("-")
            self.grid.append(row)

    def get_random_position(self):
        return (random.randint(0, len(self.grid) - 1), random.randint(0, len(self.grid[0]) - 1))

    def print_grid(self):
        for row in self.grid:
            print(' '.join(row))


class Player:
    def __init__(self, id_, initial_position=(0, 0), initial_direction="RIGHT"):
        self.id = id_
        self.position = initial_position
        self.direction = initial_direction
        self.position_history = [initial_position]

    def set_position(self, new_position):
        self.add_to_position_history(self.position)
        self.position = new_position

    def get_position(self):
        return self.position

    def set_direction(self, new_direction):
        if new_direction in POSSIBLE_DIRECTIONS:
            self.direction = new_direction

    def get_direction(self):
        return self.direction

    def get_position_history(self):
        return self.position_history[:]

    def add_to_position_history(self, position):
        if isinstance(position, tuple) and len(position) != 2:
            self.position_history.append(position)

    def get_next_position(self, grid):
        if self.direction == "RIGHT":
            new_col = self.position[1] + 1
            new_row = self.position[0]
            if new_col >= len(grid[0]):
                new_col = 0
        elif self.direction == "LEFT":
            new_col = self.position[1] - 1
            new_row = self.position[0]
            if new_col < 0:
                new_col = len(grid[0]) - 1
        elif self.direction == "UP":
            new_row = self.position[0] - 1
            new_col = self.position[1]
            if new_row < 0:
                new_row = len(grid[0]) - 1
        elif self.direction == "DOWN":
            new_row = self.position[0] + 1
            new_col = self.position[1]
            if new_row >= len(grid):
                new_row = 0
        else:
            raise Exception("INVALID POSITION")
        return new_row, new_col


def load_grid(screen, grid):
    for row_idx in range(len(grid.grid)):
        for col_idx in range(len(grid.grid[0])):
            if grid.grid[row_idx][col_idx] == "-":
                rect = get_rect((row_idx, col_idx))
                pygame.draw.rect(screen, (255, 255, 255), rect, 0)
            elif grid.grid[row_idx][col_idx].lower() == "a":
                rect = get_rect((row_idx, col_idx))
                pygame.draw.rect(screen, (0, 0, 255), rect, 0)
            elif grid.grid[row_idx][col_idx].lower() == "b":
                rect = get_rect((row_idx, col_idx))
                pygame.draw.rect(screen, (255, 0, 0), rect, 0)
            elif grid.grid[row_idx][col_idx].lower() == "x":
                rect = get_rect((row_idx, col_idx))
                pygame.draw.rect(screen, (0, 0, 0), rect, 0)


def get_rect(position):
    return pygame.Rect(position[1]*BLOCK_SIZE, position[0]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)


def main():
    game = Tron()
    # Initialise screen
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((GRID_HEIGHT*BLOCK_SIZE, GRID_WIDTH*BLOCK_SIZE))
    clock.tick(50)

    screen.fill((255, 255, 255))
    load_grid(screen, game.grid)
    pygame.display.flip()

    play_num = 0
    playing_game = True
    while playing_game and game.state == "PLAYING":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing_game = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    game.players[0].set_direction("DOWN")
                elif event.key == pygame.K_UP:
                    game.players[0].set_direction("UP")
                elif event.key == pygame.K_LEFT:
                    game.players[0].set_direction("LEFT")
                elif event.key == pygame.K_RIGHT:
                    game.players[0].set_direction("RIGHT")
                elif event.key == pygame.K_s:
                    game.players[1].set_direction("DOWN")
                elif event.key == pygame.K_w:
                    game.players[1].set_direction("UP")
                elif event.key == pygame.K_a:
                    game.players[1].set_direction("LEFT")
                elif event.key == pygame.K_d:
                    game.players[1].set_direction("RIGHT")
        play_num += 1
        updated_rects = game.turn(screen)
        pygame.display.update(updated_rects)

        time.sleep(2.5/GRID_WIDTH)

    print(game.state)


if __name__ == "__main__":
    main()
