import hlt
from hlt import constants
from hlt.positionals import Direction

import logging
from ShipActions import harvest

class GameState():
    def __init__(self):
        self.game = hlt.Game()
        self.game.ready("Helw150")
        self.updateStates()
        logging.info("Beginning Game! My Player ID is {}.".format(self.game.my_id))

    def updateStates(self):
        self.me = self.game.me
        self.game_map = self.game.game_map
        self.opponent_bases = [player.shipyard.position for player in self.game.players.values() if player != self.me]
        

    def loop(self):
        commands = []
        self.game.update_frame()
        self.updateStates()
        commands.extend(self.moveShips())
        commands.extend(self.spawn())
        self.game.end_turn(commands)

    def moveShips(self):
        ship_moves = []
        for ship in self.me.get_ships():
            ship_moves.append(harvest(self, ship))
        return ship_moves
            
    def spawn(self):
        spawns = []
        if self.game.turn_number <= 50 and self.me.halite_amount >= constants.SHIP_COST and not self.game_map[self.me.shipyard].is_occupied:
            spawns.append(self.me.shipyard.spawn())
        return spawns
