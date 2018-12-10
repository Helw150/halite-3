import hlt
from hlt import constants
from hlt.positionals import Direction
import numpy as np

import random
import logging

def harvest(game_state, ship):
    if ship.halite_amount >= 0.9*constants.MAX_HALITE or int(game_state.game_map.calculate_distance(ship.position, game_state.me.shipyard.position)*1.5) > game_state.turns_left or game_state.turns_left <= 25:
        return(returnToHome(game_state, ship))
    elif ship.position == game_state.me.shipyard.position:
        next_spot = random.choice(ship.position.get_surrounding_cardinals())
        move = game_state.game_map.smarter_navigate(ship, next_spot, game_state.futures)
        return(move)
    else:
        candidates = manhattanRadius(1, ship.position)
        next_spot = chooseBestCell(candidates, game_state, ship.position)
        move = game_state.game_map.smarter_navigate(ship, next_spot, game_state.futures)
        return(move)
        
def returnToHome(game_state, ship):
    move = game_state.game_map.smarter_navigate(ship, game_state.me.shipyard.position,game_state.futures)
    return(move)

def manhattanRadius(N, position):
    if N == 1:
        return position.get_surrounding_cardinals()
    else:
        candidates = position.get_surrounding_cardinals()
        for next_position in position.get_surrounding_cardinals():
            candidates.extend(manhattanRadius(N-1, next_position))
        return candidates

def chooseBestCell(positions, game_state, current_pos):
    hallite_amount = game_state.game_map[current_pos].halite_amount
    cost_to_move = hallite_amount * 0.1
    gained_by_stay = hallite_amount * 0.25
    position_weight_dict = game_state.position_weights
    halite_matrix = game_state.halite_matrix
    max_val = (np.sum(np.multiply(position_weight_dict[current_pos], halite_matrix))+gained_by_stay+cost_to_move)
    max_cell = current_pos
    for position in positions:
        position = game_state.game_map.normalize(position)
        value = np.sum(np.multiply(position_weight_dict[position], halite_matrix))*0.75
        if value > max_val and position != current_pos:
            max_cell = position
            max_val = value
    return max_cell
