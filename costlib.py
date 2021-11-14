"""The dark magic that generates stock prices. Put in the last price and some deep magic from before time and out will pop the next stock price"""
import random
import os


def gencost(cost):

    random.seed(os.urandom(32))
    rand = random.randint(1, 100)
    if rand > cost:
        cost = cost + random.uniform(0.3, 1.5)
    else:
        cost = cost - random.uniform(0.3, 1.5)
    cost = round(cost, 2)
    randomchance = random.randint(1, 1000)
    if randomchance == 1:
        cost += 50
    elif randomchance == 2:
        if (cost - 50) < 10:
            cost = 10
        else:
            cost -= 50
    return cost


if __name__ == '__main__':
    print(gencost(50))
