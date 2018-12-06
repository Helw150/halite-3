import hlt
from hlt import constants

import random
import logging

def harvest(game_state, ship):
    if ship.halite_amount >= 0.9*constants.MAX_HALITE:
        return(returnToHome(game_state, ship))
    elif ship.position == game_state.me.shipyard.position:
        next_spot = random.choice(ship.position.get_surrounding_cardinals())
        move = game_state.game_map.smarter_navigate(ship, next_spot, game_state.futures)
        return(move)
    else:
        candidates = manhattanRadius(2, ship.position)
        next_spot, next_hal = chooseBestCell(candidates, game_state.game_map, ship.position)
        move = game_state.game_map.smarter_navigate(ship, next_spot, game_state.futures)
        return(move)
        
def returnToHome(game_state, ship):
    move = game_state.game_map.smarter_navigate(ship, game_state.me.shipyard.position, game_state.futures)
    return(move)

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
            max_hal = game_map[max_cell].halite_amount
    return max_cell, max_hal
