import hlt
from hlt import constants
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
        still_ships = [ship for ship in ships if ship.halite_amount < self.game_map[ship.position].halite_amount*0.1]
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
        self.futures = []
            
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
        self.futures.append(future_pos)
        logging.info(self.futures)
        
    def moveShips(self):
        moves = []
        still_ships, ships_to_move = self.shipsByMovingStatus()
        for ship in still_ships:
            self.futures.append(ship.position)
        for ship in ships_to_move:
            move = harvest(self, ship)
            self.addToFuture(ship, move)
            moves.append(ship.move(move))
        return moves

    def spawn(self):
        spawns = []
        if self.game.turn_number <= self.turns-self.end_repro and self.me.halite_amount >= constants.SHIP_COST and self.me.shipyard.position not in self.futures:
            self.futures.append(self.me.shipyard.position)
            spawns.append(self.me.shipyard.spawn())
        return spawns
