import random


def chance(n):
    choices = []
    for x in range(n - 1):
        choices.append(False)
    choices.append(True)
    return random.choice(choices)


def recipes():
    # region Recipes
    crafts = {
        # Any line that starts with a hash (#) is a comment; what is on that line does not impact the code. It is used to describe the code so feel free to add your own

        # The first part of the craft syntax is the name. In the template below it is is example. The second part is the ingrediants. Each item inside it conatains the item type, the amount needed and whether or not to consume the ingrediant on craft. If True it will bo consumed and if it is False it will not. If you leave the third section blank it will default to consuming the item. The third part of the main recipe (not inside an ingrediant) is how long it takes to craft in seconds. The forth is how many you get from crafting it. If left blank it will default to one. The fith part is the alternative result. If specified, the result will be the fith part, not the name of the recipe.

        # To add you own crafts is very simple. Just copy the template from below without the hashes of course.

        # "example": [[["metal", 3, True], ["wood", 2, True]], 10, 5, "stone"],

        # just replace the "example" with what you want the name of the new item
        # names are case sensitive so make sure you get it right. Also the commas, brackets and quote marks are vital so make sure you don't leave them out. You also need to add a comma to the end of each item
        # you can also have other crafted items as ingrediants (eg, one item called "oil" and you need 10 oil to make a car). Its pretty easy to do this; just change the ingrediant's name to that of another material
        # For people editing: format is "name": [[["mat 1", count], ["mat 2", count, <whether to consume (bool)>]] time to craft, <amount gained>, <alt result>]
        # example:

        # "oil": [["wood", 10, True], ["metal", 8, True]],
        # "car": [["oil", 10], ["metal", 10]], (Even though this one does not have the consume specifier, it will still consume it)

        # that would be a valid item
        # if you have a github account simply fork the repo (look up how), add the new items then create a pull requests and ping me on discord.
        # if you don't copy the formatting and send your ideas to me over discord.
        # Just some other stuff:
        # 1. make sure all names are lowercase and don't contain spaces
        # 2. no offesive stuff
        # 3. Please don't have people as an option since we will be selling them. Thats not legal anymore
        # 4. Keep it inside the curly brackets

        # chance(number)

        "base-pick": [[["stone", 3], ["organics", 1]], 5],
        "base-shovel": [[["stone", 2], ["organics", 1]], 5],
        "sand": [[["base-shovel", 1]], 10, 5],
        "copper-ore": [[["base-pick", 1]], 10, 10],
        "oil": [[["organics", 10]], 300, 1],
        "coal": [[["organics", 10]], 300, 1],
        "lead": [[["base-pick", 1]], 10, 10],
        "tin": [[["base-pick", 1]], 10, 10],
        "forge": [[["stone", 10], ["organics", 3]], 60],
        "glass": [[["sand", 10], ["forge", 1, False]], 15],
        "bottle": [[["glass", 2]], 5, 1],
        "iron-plate": [[["iron-ore", 5], ["forge", 1, False]], 20],
        "anvil": [[["iron-plate", 15]], 120],
        "iron-plate-level-2": [[["iron-ore", 2], ["forge", 1, False], ["anvil", 1, False]], 10, 1, "iron-plate"],
        "copper-plate": [[["copper-ore", 2], ["forge", 1, False], ["anvil", 1, False]], 10],
        "wire": [[["copper-plate", 1], ["anvil", 1, False]], 10, 5],
        "circuits": [[["wire", 5], ["silicon", 1]], 20, 2],
        "electric-forge": [[["wire", 15], ["circuits", 10], ["iron-plate", 20], ["copper-plate", 20], ["anvil", 1, False], ["forge", 1]], 120],
        "silicon": [[["sand", 10], ["electric-forge", 1, False]], 20],
        "iron-pick": [[["iron-plate", 3], ["organics", 1], ["electric-forge", 1, False]], 60],
        "copper-ore-level-2": [[["iron-pick", 1, False]], 5, 10, "copper-ore"],
        "coal-level-2": [[["friend", 5, chance(2)], ["iron-pick", 5]], 45, 20, "coal"],
        "loom": [[["organics", 5], ["iron-ore", 2]], 15],
        "biotank": [[["iron-plate", 30], ["circuits", 10], ["glass", 50]], 60],
        "friend": [[["biotank", 1, False], ["organics", 50], ["circuits", 3]], 120],
        "cotton": [[["friend", 1, chance(5)], ["organics", 10]], 25, 10],
        "string": [[["cotton", 5], ["loom", 1, False]], 10, 3],
        "iron-ore-level-2": [[["friend", 5, chance(5)], ["iron-pick", 5]], 45, 20, "iron-ore"],
        "solder": [[["lead", 5], ["tin", 5], ["electric-forge", 1, False]], 10, 3],
        "assembler": [[["iron-plate", 10], ["circuits", 3], ["wire", 10], ["glass", 4], ["friend", 1]], 60],
        "prossessor": [[["solder", 6], ["circuits", 2], ["wire", 5], ["assembler", 1, False]], 20],
        "3089": [[["solder", 3], ["silicon", 5], ["prossessor", 12], ["assembler", 1, False], ["iron-plate", 1]], 130, 1],
        "vodka": [[["bottle", 1], ["organics", 2]], 10, 1],
        "ram": [[["prossessor", 1], ["circuits", 10], ["assembler", 1, False]], 45, 1],
        "plastic": [[["assembler", 1, False], ["oil", 1]], 100],
        "h8": [[["assembler", 1, False], ["prossessor", 5], ["wire", 5], ["silicon", 3], ["friend", 1]], 90],
        "gaming-computer": [[["assembler", 5, False], ["plastic", 10], ["ram", 4], ["3089", 2], ["h8", 2], ["friend", 1], ["wire", 10]], 200],
        "chrome-tab": [[["ram", 100]], 1],
        "router": [[["plastic", 10], ["circuits", 5]], 10, 1],
        "internet": [[["router", 1, chance(20)], ["gaming-computer", False]], 120, 20],
        "turbo-virgin": [[["gaming-computer", 1], ["internet", 1], ["friend", 1]], 60, 1],
        "download-ram": [[["chrome-tab", 1], ["gaming-computer", 1, False], ["internet", 1]], 60, 10, "ram"],
        "arc-forge": [[["electric-forge", 10], ["gaming-computer", 1], ["coal", 10], ["stone", 500], ["wire", 15]], 200, 1],
        "iron-plate-level-3": [[["arc-forge", 1, False], ["iron-ore", 30]], 5, 30, "iron-plate"],
        "copper-plate-level-3": [[["arc-forge", 1, False], ["copper-ore", 30]], 5, 30, "copper-plate"],
        "mining-system": [[["assembler", 2], ["arc-forge", 2], ["prossessor", 3], ["iron-plate", 30], ["friend", 3]], 60, 1],
        "iron-ore-level-3": [[["mining-system", 1, chance(100)], ["friend", 10, chance(30)], ["water", 20]], 20, 100, "iron-ore"],
        "copper-ore-level-3": [[["mining-system", 1, chance(100)], ["friend", 10, chance(30)], ["water", 20]], 20, 100, "copper-ore"],
        "stone-level-3": [[["mining-system", 1, chance(100)], ["friend", 10, chance(30)], ["water", 20]], 20, 100, "stone"],
        "coal-level-3": [[["mining-system", 1, chance(100)], ["friend", 10, chance(30)], ["water", 20]], 20, 100, "coal"],
        "rootyle": [[["mining-system", 1, chance(50)], ["friend", 10, chance(30)], ["water", 20]], 20, 100, "titanium-ore"],
        "piston-engine": [[["iron-plate", 20]]]
    }

    return crafts
