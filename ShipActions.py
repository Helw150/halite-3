import hlt
from hlt import constants

import random
import logging

def harvest(game_map, ship):
    if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
        next_spot = random.choice(ship.position.get_surrounding_cardinals())
        move = game_map.naive_navigate(ship, next_spot)
        return(ship.move(move))
    elif ship.halite_amount >= constants.MAX_HALITE / 4:
        move = game_map.naive_navigate(ship, me.shipyard.position)
        return(ship.move(move))
    else:
        return(ship.stay_still())
