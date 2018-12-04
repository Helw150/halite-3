import hlt
from hlt import constants
from hlt.positionals import Direction

import logging
from ShipActions import harvest, assasinate

widthToTurns = {32:400, 40:425, 48:450, 56:475, 64:500}
class GameState():
    def __init__(self, end_repro=300, assasins=True):
        self.end_repro = end_repro
        self.game = hlt.Game()
        self.me = self.game.me
        self.width = self.game.game_map.width
        self.turns = widthToTurns[self.width]
        self.assasins = {}
        self.opponent_bases = [player.shipyard.position for player in self.game.players.values() if player != self.me]
        self.updateStates()
        self.game.ready("Helw150")
        logging.info("Beginning Game! My Player ID is {}.".format(self.game.my_id))

    def updateStates(self):
        self.me = self.game.me
        self.game_map = self.game.game_map
        self.createAssasins()
        
    def createAssasins(self):
        logging.info(len(self.me.get_ships()))
        for ship in list(self.assasins.keys()):
            if ship not in [ship.id for ship in self.me.get_ships()]:
                target = self.assasins[ship]
                del(self.assasins[ship])
                self.opponent_bases.append(target)
        if self.opponent_bases != [] and len(self.me.get_ships()) - len(self.assasins) > 5:
            for ship in sorted(self.me.get_ships(), key=lambda x: x.halite_amount):
                if ship.halite_amount == 0 and ship not in self.assasins:
                    if self.opponent_bases != []:
                        self.assasins[ship.id] = self.opponent_bases.pop()
        logging.info(self.assasins)
            
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
            if ship.id not in self.assasins:
                ship_moves.append(harvest(self, ship))
            else:
                ship_moves.append(assasinate(self, ship, self.assasins[ship.id]))
        return ship_moves
            
    def spawn(self):
        spawns = []
        if self.game.turn_number <= self.turns-self.end_repro and self.me.halite_amount >= constants.SHIP_COST and not self.game_map[self.me.shipyard].is_occupied:
            spawns.append(self.me.shipyard.spawn())
        return spawns
