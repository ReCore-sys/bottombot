"""The dark magic that generates stock prices. Put in the last price and some deep magic from before time and out will pop the next stock price"""
import os
import random

import botlib


def gencost(cost):

    random.seed(os.urandom(32))
    rand = random.randint(1, 100)
    upper = botlib.configs("stocks", "upper")
    lower = botlib.configs("stocks", "lower")
    jumpup = botlib.configs("stocks", "jumpup")
    jumpdown = botlib.configs("stocks", "jumpdown")
    if rand > cost:
        cost += random.uniform(lower, upper)
    else:
        cost -= random.uniform(lower, upper)
    cost = round(cost, 2)
    randomchance = random.uniform(0, 1)
    if randomchance < jumpup:
        print("Jumped up")
        cost += 50
    elif randomchance < jumpdown:
        print("Jumped down")
        if (cost - 50) < 10:
            cost = 10
        else:
            cost -= 50
    return cost


if __name__ == "__main__":
    print(gencost(50))
