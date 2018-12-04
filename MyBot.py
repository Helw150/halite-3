#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Direction

import random
import logging

game = hlt.Game()
game.ready("Helw150")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

me = game.me
opponent_bases = [player.shipyard.position for player in game.players.values() if player != me]
logging.info(opponent_bases)
logging.info(me.shipyard.position)
while True:
    game.update_frame()
    me = game.me
    game_map = game.game_map
    
    command_queue = []
    for ship in me.get_ships():
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            next_spot = random.choice(ship.position.get_surrounding_cardinals())
            move = game_map.naive_navigate(ship, next_spot)
            command_queue.append(ship.move(move))
        else:
            command_queue.append(ship.stay_still())

    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)

