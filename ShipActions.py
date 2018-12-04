import hlt
from hlt import constants

import random
import logging

def manhattanRadius(N, position):
    if N == 1:
        return position.get_surrounding_cardinals()
    else:
        candidates = position.get_surrounding_cardinals()
        for next_position in position.get_surrounding_cardinals():
            candidates.extend(manhattanRadius(N-1, next_position))
        return candidates

def chooseBestCell(positions, game_map, current_pos):
    max_cell = current_pos
    max_hal = game_map[max_cell].halite_amount*3
    for position in positions:
        if game_map[position].halite_amount > max_hal and position != current_pos:
            max_cell = position
            logging.info((position, current_pos))
            max_hal = game_map[max_cell].halite_amount
    return max_cell, max_hal
    
def harvest(game_state, ship):
    current_position_halite = game_state.game_map[ship.position].halite_amount
    current_cost = 0.1 * current_position_halite
    if ship.halite_amount >= 0.9*constants.MAX_HALITE:
        return(returnToHome(game_state, ship))
    elif ship.halite_amount >= current_cost:
        candidates = manhattanRadius(2, ship.position)
        next_spot, next_hal = chooseBestCell(candidates, game_state.game_map, ship.position)
        move = game_state.game_map.naive_navigate(ship, next_spot)
        if ship.move(move) == ship.stay_still() and ship.position == game_state.me.shipyard.position:
            for position in ship.position.get_surrounding_cardinals():
                move = game_state.game_map.naive_navigate(ship, position)
                if ship.move(move) != ship.stay_still():
                    break
        return(ship.move(move))
    else:
        return(ship.stay_still())


def returnToHome(game_state, ship):
    move = game_state.game_map.naive_navigate(ship, game_state.me.shipyard.position)
    if ship.move(move) == ship.stay_still():
            for position in ship.position.get_surrounding_cardinals():
                move = game_state.game_map.naive_navigate(ship, position)
                if ship.move(move) != ship.stay_still():
                    break
    return(ship.move(move))
