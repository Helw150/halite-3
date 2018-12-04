import hlt
from hlt import constants
from hlt.positionals import Direction

import random
import logging

def manhattanRadius(N, position):
    if N == 1:
        candidates = position.get_surrounding_cardinals()
    else:
        candidates = position.get_surrounding_cardinals()
        for next_position in position.get_surrounding_cardinals():
            candidates.extend(manhattanRadius(N-1, next_position))
    return candidates

def chooseBestCell(positions, game_map, current_pos):
    max_cell = current_pos
    max_hal = game_map[max_cell].halite_amount*3
    for position in positions:
        adjusted_hal = game_map[position].halite_amount
        if  adjusted_hal > max_hal and position != current_pos:
            max_cell = position
            max_hal = game_map[max_cell].halite_amount
    return max_cell
    
def harvest(game_state, ship):
    current_position_halite = game_state.game_map[ship.position].halite_amount
    current_cost = 0.1 * current_position_halite
    if ship.halite_amount >= 0.9*constants.MAX_HALITE:
        return(returnToHome(game_state, ship))
    elif ship.position == game_state.me.shipyard.position:
        move = game_state.start()
        return(ship.move(move))
    elif ship.halite_amount >= current_cost:
        candidates = manhattanRadius(2, ship.position)
        next_spot = chooseBestCell(candidates, game_state.game_map, ship.position)
        move = game_state.game_map.naive_navigate(ship, next_spot)
        return(ship.move(move))
    else:
        return(ship.stay_still())


def assasinate(game_state, ship, target):
    current_position_halite = game_state.game_map[ship.position].halite_amount
    current_cost = 0.1 * current_position_halite
    logging.info("Assasin Ship {}".format(ship))
    logging.info("Assasin Target {}".format(target))
    move = game_state.game_map.naive_navigate(ship, target)
    if ship.move(move) == ship.stay_still() and ship.position != target:
            for position in ship.position.get_surrounding_cardinals():
                move = game_state.game_map.naive_navigate(ship, position)
                if ship.move(move) != ship.stay_still():
                    break
    if ship.halite_amount >= current_cost:
        return(ship.move(move))
    else:
        return(ship.stay_still())
    
def returnToHome(game_state, ship):
    above_yard = game_state.me.shipyard.position.directional_offset(Direction.North)
    below_yard = game_state.me.shipyard.position.directional_offset(Direction.South)
    if ship.position.y < game_state.me.shipyard.position.x:
        if ship.position not in below_yard.get_surrounding_cardinals():
            move = game_state.game_map.naive_navigate(ship, below_yard)
        else:
            move = game_state.game_map.get_unsafe_moves(ship, below_yard)
    elif ship.position.y >= game_state.me.shipyard.position.x:
        if ship.position not in above_yard.get_surrounding_cardinals():
            move = game_state.game_map.naive_navigate(ship, above_yard)
        else:
            move = game_state.game_map.get_unsafe_moves(ship, above_yard)
    elif ship.position == above_yard or ship.position == below_yard:
        move = game_state.game_map.get_unsafe_moves(ship, game_state.me.shipyard.position)
    return(ship.move(move))
