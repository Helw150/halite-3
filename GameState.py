'''
This file is the high level bot strategy for the full fleet 
of ships (or turtles!) in my Halite 3 Bot. It also houses the logic
for transferring state from the hlt package provided by TwoSigma to formats that I find more usable.
'''
import hlt
from hlt import constants
from hlt.positionals import Direction, Position
from ShipActions import harvest
import numpy as np

import logging

# Map from width of the map to the number of turns in the game
widthToTurns = {32:400, 40:425, 48:450, 56:475, 64:500}

class GameState():
    def __init__(self):
        self.game = hlt.Game()
        self.spawningParams()
        self.updateStates()
        self.createPositionWeights()
        self.game.ready("Helw150")
        logging.info("Beginning Game! My Player ID is {}.".format(self.game.my_id))

    # High level operations that are run each turn
    def loop(self):
        commands = []
        self.game.update_frame()
        self.updateStates()
        commands.extend(self.moveShips())
        commands.extend(self.spawn())
        logging.info(commands)
        self.game.end_turn(commands)
    
    # Populates the weight matrix based on distance from the center of the map
    def createPositionWeights(self):
        origin = Position(0,0)
        origin_distance_matrix = np.zeros((self.width, self.width), dtype=float)
        # Creates basic distance matrix
        for x in range(self.width):
            for y in range(self.width):
                next_position = Position(x, y)
                distance = float(self.game_map.calculate_distance(origin, next_position))
                offset = 1
                if distance == 0:
                    offset = 0
                origin_distance_matrix[x][y] = float(self.game_map.calculate_distance(origin, next_position)) + offset
        # Exponential function to balance local and global focus
        # FUTURE: Tune this with TPOT package rather than by hand
        origin_weight_matrix = (0.4)**origin_distance_matrix
        self.position_weights = {origin: origin_weight_matrix}
        # Use roll to quickly create weight matrix for every position in the map
        for x in range(self.width):
            for y in range(self.width):
                position = Position(x, y)
                weight_matrix_horizontal_shifted = np.roll(origin_weight_matrix, x, axis=0)
                weight_matrix_shifted = np.roll(weight_matrix_horizontal_shifted, y, axis=1)
                self.position_weights[position] = weight_matrix_shifted
                

    # Pass data from internal to custom state manager
    def updateHaliteMatrix(self):
        self.halite_matrix = self.game_map.halite_matrix
        logging.info(self.halite_matrix)

    # State setup for spawning of new shapes
    # FUTURE: Tune with TPOT rather than by hand
    def spawningParams(self):
        self.end_repro = 200
        self.width = self.game.game_map.width
        self.turns = widthToTurns[self.width]
        self.max_ships = self.turns*.075

    # Split ships by whether or not they can afford the cost to move
    def shipsByMovingStatus(self):
        ships = self.me.get_ships()
        # Ships that have no choice but to stay still
        still_ships = [ship for ship in ships if ship.halite_amount < self.game_map[ship.position].halite_amount*0.1 and self.game_map[ship.position].halite_amount != 0]
        ships_to_move = [ship for ship in ships if ship not in still_ships]
        # FUTURE: This is meant to help the collision avoidance algorithm avoid collisions with fewer recursions.
        # It does so somewhat, but really I want to cluster the ships so that collision avoidance schedules them in
        # batches somehow. Doubt it would actually be a huge performance increase so saving for later.
        ships_to_move.sort(key = lambda x: self.game_map.calculate_distance(x.position, self.me.shipyard.position))
        return still_ships, ships_to_move

    # State transfer and reformating from Halite internals
    def get_halite_grid(self):
        self.halite_values = []
        for row in self.game_map._cells:
            row_halite = []
            for cell in row:
                row_halite.append(cell.halite_amount)
            self.halite_values.append(row_halite)

    # Turn by turn state update
    def updateStates(self):
        self.me = self.game.me
        self.game_map = self.game.game_map
        self.updateHaliteMatrix()
        self.futures = {}

    # Get the position the ship is planning to move to in the next turn and store it in state
    def addToFuture(self, ship, direction):
        logging.info(self.futures)
        future_pos = ship.position.directional_offset(direction)
        if future_pos in self.futures:
            self.futures[future_pos].append((ship, direction))
            self.futures[future_pos].sort(key=lambda x: x[0].position != future_pos)
        else:
            self.futures[future_pos] = [(ship, direction)]
        logging.info(self.futures)

    # Move ships towards targets while avoiding collisions with friendly ships
    def moveShips(self):
        still_ships, ships_to_move = self.shipsByMovingStatus()
        for ship in still_ships:
            self.addToFuture(ship, Direction.Still)
        for ship in ships_to_move:
            # This if condition overrides collision avoidance for the end game
            # so that ships will kamikaze all of the collected resources into the base
            # before the final turn.
            if ship.position != self.me.shipyard.position or self.turns_left > 25:
                move = harvest(self, ship)
                self.addToFuture(ship, move)
        # Keep re-routing colliding friendly ships until no friendly ships collide
        while self.collisionDetected():
            self.collisionResolve()
        return self.enactFuture()

    # Detect if two friendly ships have the same future position
    def collisionDetected(self):
        for residing_ships in self.futures.values():
            if len(residing_ships) > 1:
                return True
        return False

    # Re-route ships that are currently on course for collision
    def collisionResolve(self):
        ships_to_resolve = []
        for position in self.futures:
            residing_ships = self.futures[position]
            if len(residing_ships) > 1:
                self.futures[position] = [residing_ships[0]]
                ships_to_resolve.extend(residing_ships[1:])
        for ship, _ in ships_to_resolve:
            move = harvest(self, ship)
            self.addToFuture(ship, move)

    # Convert the future positions into commands for the game engine
    def enactFuture(self):
        moves = []
        for position in self.futures:
            ship, move = self.futures[position][0]
            moves.append(ship.move(move))
        return moves

    # Helper for the number of turns still in the game
    @property
    def turns_left(self):
        return self.turns-self.game.turn_number

    # Rules which define whether or not to spawn new ships
    def spawn(self):
        spawns = []
        if self.turns_left >= self.end_repro and self.me.halite_amount >= constants.SHIP_COST and self.me.shipyard.position not in self.futures and len(self.me.get_ships()) < self.max_ships:
            spawns.append(self.me.shipyard.spawn())
        return spawns
