import random


def gencost(cost):
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
