import hlt
from hlt import constants
from hlt.positionals import Direction
from ShipActions import harvest

import logging
widthToTurns = {32:400, 40:425, 48:450, 56:475, 64:500}

class GameState():
    def __init__(self):
        self.game = hlt.Game()
        self.updateStates()
        self.spawningParams()
        self.game.ready("Helw150")
        logging.info("Beginning Game! My Player ID is {}.".format(self.game.my_id))

    def spawningParams(self):
        self.end_repro = 300
        self.width = self.game.game_map.width
        self.turns = widthToTurns[self.width]
        
    def shipsByMovingStatus(self):
        ships = self.me.get_ships()
        still_ships = [ship for ship in ships if ship.halite_amount < self.game_map[ship.position].halite_amount*0.1 and self.game_map[ship.position].halite_amount != 0]
        ships_to_move = [ship for ship in ships if ship not in still_ships]
        return still_ships, ships_to_move
        
    def get_halite_grid(self):
        self.halite_values = []
        for row in self.game_map._cells:
            row_halite = []
            for cell in row:
                row_halite.append(cell.halite_amount)
            self.halite_values.append(row_halite)
        
    def updateStates(self):
        self.me = self.game.me
        self.game_map = self.game.game_map
        self.futures = {}
            
    def loop(self):
        commands = []
        self.game.update_frame()
        self.updateStates()
        commands.extend(self.moveShips())
        commands.extend(self.spawn())
        logging.info(commands)
        self.game.end_turn(commands)


    def addToFuture(self, ship, direction):
        logging.info(self.futures)
        future_pos = ship.position.directional_offset(direction)
        if future_pos in self.futures:
            self.futures[future_pos].append((ship, direction))
            self.futures[future_pos].sort(key=lambda x: x[0].position != future_pos)
        else:
            self.futures[future_pos] = [(ship, direction)]
        logging.info(self.futures)
        
    def moveShips(self):
        still_ships, ships_to_move = self.shipsByMovingStatus()
        for ship in still_ships:
            self.addToFuture(ship, Direction.Still)
        for ship in ships_to_move:
            move = harvest(self, ship)
            self.addToFuture(ship, move)
        while self.collisionDetected():
            self.collisionResolve()
        return self.enactFuture()

    def collisionDetected(self):
        for residing_ships in self.futures.values():
            if len(residing_ships) > 1:
                return True
        return False

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

    def enactFuture(self):
        moves = []
        for position in self.futures:
            ship, move = self.futures[position][0]
            moves.append(ship.move(move))
        return moves
            
    def spawn(self):
        spawns = []
        if self.game.turn_number <= self.turns-self.end_repro and self.me.halite_amount >= constants.SHIP_COST and self.me.shipyard.position not in self.futures:
            spawns.append(self.me.shipyard.spawn())
        return spawns
