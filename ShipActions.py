'''
This file controls all ship by ship behaviour for this Halite 3 bot, except for smarter_navigate which was the only modification I made to the vanilla hlt package.
'''
import hlt
from hlt import constants
from hlt.positionals import Direction
import numpy as np

import random
import logging

# Boolean check for whether a ship should return to base
def returnCondition(game_state, ship):
    # Conditions for normal harvesting behaviour
    min_hal = ship.halite_amount >= 0.9*constants.MAX_HALITE
    hal_ratio = game_state.game_map[ship.position].halite_amount <= 0.18 * ship.halite_amount
    # Two conditions for end-game kamikaze ship strategy
    return_for_end = int(game_state.game_map.calculate_distance(ship.position, game_state.me.shipyard.position)*1.5) > game_state.turns_left
    emergency_return = game_state.turns_left <= 25
    return (min_hal and hal_ratio) or return_for_end or emergency_return or ship.is_full

# High level access point from ShipActions to the rest of the bot
def harvest(game_state, ship):
    if returnCondition(game_state, ship):
        # Bring resources back to base
        return(returnToHome(game_state, ship))
    elif ship.position == game_state.me.shipyard.position:
        # Move ships randomly from the spawn to add a
        # stochastic exploration element
        next_spot = random.choice(ship.position.get_surrounding_cardinals())
        move = game_state.game_map.smarter_navigate(ship, next_spot, game_state.futures)
        return(move)
    else:
        # Move to the surrouding position with the
        # best value as determined by chooseBestCell
        candidates = manhattanRadius(1, ship.position)
        next_spot = chooseBestCell(candidates, game_state, ship.position)
        # Smarter navigate avoids placing two ships in the same
        # position by using the values of game_state.futures
        move = game_state.game_map.smarter_navigate(ship, next_spot, game_state.futures)
        return(move)

# Sends ship back to the spawn
def returnToHome(game_state, ship):
    move = game_state.game_map.smarter_navigate(ship, game_state.me.shipyard.position,game_state.futures)
    return(move)

# Helper function to get positions in a radius, but with only manhattan moves available
def manhattanRadius(N, position):
    if N == 1:
        return position.get_surrounding_cardinals()
    else:
        candidates = position.get_surrounding_cardinals()
        for next_position in position.get_surrounding_cardinals():
            candidates.extend(manhattanRadius(N-1, next_position))
        return candidates

# Game state evaluator which multiplies the halite amounts on the map by the distance-weight matrix to quickly evaluate how valuable a particular position on the map is
def chooseBestCell(positions, game_state, current_pos):
    hallite_amount = game_state.game_map[current_pos].halite_amount
    # Cost to move as defined by the game engine - not tunable
    cost_to_move = hallite_amount * 0.1
    # How much the ship would harvest defined by the game engine -  not tunable
    gained_by_stay = hallite_amount * 0.25
    position_weight_dict = game_state.position_weights
    halite_matrix = game_state.halite_matrix
    # The opportunity cost for moving to any other cell from the current position
    max_val = (np.sum(np.multiply(position_weight_dict[current_pos], halite_matrix))+gained_by_stay+cost_to_move)
    max_cell = current_pos
    for position in positions:
        position = game_state.game_map.normalize(position)
        # Give occupied positions a 0 value
        position_free = int(not position in game_state.futures)
        # FUTURE: 0.75 is a hand tuned weight and should be done with TPOT instead
        value = np.sum(np.multiply(position_weight_dict[position], halite_matrix))*0.75*position_free
        if value > max_val and position != current_pos:
            max_cell = position
            max_val = value
    # Return the highest value move the ship has at the moment
    return max_cell
