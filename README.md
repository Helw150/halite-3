# Halite 3 Bot Competition Entry

## Introduction
Halite is a yearly bot programming competition put on by Two Sigma. Each year it seems to take shape as a competitive resource collection game. I became aware of it for the first time this year, after seeing a tweet from Camille Fournier about the competition. I spent around a week working a few hours a day on my bot mostly focused on developing strategies inspired by some articles on Computational strategies for chess and trying as best as I could do to emulate specific behaviors of some of the top bots on the leaderboard.

So without further ado, here are the key behaviours of my bot that eventually peaked as high as the top #300 out of ~4000 entrants (since December I have fallen to #385 presumably as people have continued to improve their bots).

**NOTE: All code in the hlt directory is from the TwoSigma provided package that provides an abstraction around the language agnostic game engine except for one function called `smarter_navigate` which is my personal improvement on the base function called `naive_navigate`**

### Prior reading & Watching to become familiar with this years Halite
I don't think I'll be able to do a much better job describing the game than the creators themselves so I'd highly reccomend checking out [this page on the Halite website before reading this doc](https://halite.io/learn-programming-challenge/game-overview). Additionally, I would reccomend watching my bot in action on the Halite competitions website - you can watch replays by clicking on any of the replays found [here](https://halite.io/user/?user_id=7298) or simply watch [this game in particular](https://halite.io/play/?game_id=5168616&replay_class=1&replay_name=replay-20190125-225245%2B0000-1548456751-40-40-5168616) where my bot, the pink team on the bottom right, wins in a 4 player match.

## Individual Ship Movement
Individual ship movement is the first thing I worked on in the competition and makes the largest impact of any factor in my climb through the Halite ranks. The first aspect of how your ships move is how where and when they decide to move each turn as they seek to collect resources. The second aspect which is slightly easier is when your ships decide to return their resoures to the spawn so collected resources can be put to use.

### Target Selection
Target selection is the process of a ship choosing where it should move to maximize the amount of resources it can collect in its life. Since this was my first time competing in a competitive programming competition specifically for a competitive game, I tried to read about the common strategies in the field, and for all games the first step was creating something that could score moves quickly based on the board state.

In my first multiple iterations using a minimax inspired recursive strategy for evaluating the next move, I consistently ran into the same problem - the depth of recursion possible in the time limit for each turn in the Halite competition was not particularly useful. Especially in the end of the game, when there can be 30+ ships all with decisions that need to be made no deep recursion is possible in the the time limit so all ships end up making very decisions that are very locally focused and aren't much better than a naive target selection of moving to the neighboring square with the most halite. This isn't as large a problem in Chess for example, where only one move is made every turn and in non-bullet matches decisions happen at a much slower pace.

As I began to think more about how to create an evaluation function which didn't require deep recursion to provide global context to the value of each move, I couldn't get away from the fact that the board itself was a matrix ripe with linear algebra applications. Eventually, my evaluation function became the one that can be found in `ShipActions.chooseBestCell` which exploits numpy's fast C-accelerated matrix multiplication to calculate the value of each square to reward moves that both place the ship closer to high value cells for long term value and cells with at least reasonable reward in the short term.

In this evaluation function, each square, the origin of the weight matrix, has an associated "weight matrix" for all other squares on the map, the targets of the weight matrix. This weight matrix can be simply understood to give lower weights to targets that are further away from the origin. Code for the creation of this matrix can be found at `GameState.createPositionWeights`. This matrix is then multiplied with the amount of resources there is in each cell. Finally, the cells of the resultant matrix are summed to create the value of the cell. This way the short term reward is valued more highly than the long term reward, but the ship is still influenced in the direction of long term high reward value.

### Return Conditions

Return conditions inform when a ship is ready to return with the Halite it has harvested. The simplest check for this is to wait for the ship to collect as much Halite as it can hold (1000), but this can cripple your ability to spawn ships early since your ships are stuck waiting to reach exactly 1000. However, simply decreasing this threshold (which in my code is set by `min_hal` in `ShipActions.returnCondition` often leads to behavior where ships try to return even when they are in a high value area which is expensive to leave. Therefore, the `hal_ratio` return condition protects against this, keeping ships from returning when they are on cells with greater than 18% of their current Halite. 

## Fleet Management
Fleet management is a very close second in importance to individual ship logic as it can have catastrophic downsides so if a Halite bot has poor fleet management it is more likely to be dominated by edge-case opponents or maps. For a succesful Halite bot your individual ships must avoid colliding one another and therefore destroying expensive shipes and not create traffic deadlocks amongst themselves which can halt the entire harvesting process. 

### Collision Avoidance
When two ships in Halite both attempt to move to the same square in the same turn, they collide and both ships are destroyed with their harvested resources left in the square they collided in. For bots ranked 200 and higher, this becomes an important combat tool, but up until that point the primary concern is keeping your own ships from running into eachother.

The Two Sigma team provided a function to assist with this called `naive_navigate` which will keep a ship from moving if the move would cause a collision. This function appeared tremendously useful at the beginning of the competition, when collisions seemed very wasteful. However, while collisions are painful, more painful are the types of deadlock which `naive_navigate` can cause which both effectively destroy the deadlocked ships and leave them as a risk to deadlock your other ships. A great example of this is from an earlier version of my bot. In [this](game), a deadlock occurs towards the middle of the match in the top left corner and it effectively cripples me because `naive_navigate` has no method for deadlock resolution.

To decrease the effects of this, I decided to update my movement code to use a system I called *futures*. Before any commands are issued to the game engine, I first calculate where each ship would be going if it moved in isolation. Inevitably, some ships which are nearby eachother would ideally move to the same high value squares if they moved in isolation. This would cause a collision, so in the futures methodology instead of having a ship that would move into a collision simply hold still - which often causes a deadlock - the ship selects a new target which avoids the collision. This process is run in a while loop until all ships have a target that does not cause a collision. Only once this happens are commands actually issued to the game engine, thereby enacting this future. This process almost entirely eliminated deadlocks for my bot and yielded other improvements to the overall movement of my fleet. The code for this functionality is pervasive, but the high level code controlling the process lies in `GameState.moveShips`.

### Spawning Logic
Similar to returning logic, the logic of when it is worth it to spend halite building a new ship can largely be controlled by threshold logic. For my bot, I spawn ships every turn I can afford to until 200 turns from the final turn. This value was tuned according to the asymptotic behaviour of the resource harvesting at the time you stop producing new ships. I found an easy way to check whether my threshold was common sense was observing this asymptotic behaviour on the graph to the right of the replay viewer. In many Halite 3 games, you can see that people simply overproduce ships, and are never able to catch up in savings to those that stop production at a better tuned value. A good example of this is in [this game](https://halite.io/play/?game_id=5167728&replay_class=1&replay_name=replay-20190125-223156%2B0000-1548455468-40-40-5167728), where the second place player loses almost purely because they over-produced ships.

All the code for spawning logic is held in `GameState.spawn` and `GameState.spawningParams`.

## Running this code
The easiest way to view this code running is submitting as a zip file to the Halite website and viewing it there.

However, local development testing can be set up using the `run-game.sh` script. However, you have to download the `./halite` binary from the tools section of the [Halite's download page](https://halite.io/learn-programming-challenge/downloads) near the bottom of the page.