
def help(cmd = None):
    helper = {
        "Music": {
            "connect": "Connect to a voice channel.",
            "play": "(-play [song link or name]\nPlay or queue a song with the given query.",
            "pause": "Pause the currently playing song.",
            "resume": "Resume the currently paused song.",
            "skip": "Skip the currently playing song.",
            "stop": "Stop and reset the music player.",
            "volume": "(-volume <number>)\nChange the music player's volume, between 1 and 100.",
            "shuffle": "Shuffle the music player's queue.",
            "queue": "Display's the music player's queued songs.",
            "nowplaying": "Show the currently playing song.",
            "swap_dj": "Swap the current DJ to another member in the voice channel.",
            "equaliser": "music filters that are still under dev"},
        "Cross Server Chat": {
            "join": "Adds you to the waiting list of servers wanting to chat. Also sets the current channel as the conversation channel.",
            "leave": "If you are in the waiting list, it will remove you from it. If you are currently connected to another server it will disconnect you."},
        "Economy": {
            "balance": "(-balance <user>)\nShows the bank account of the pinged user. If none pinged will show your own.",
            "pay": "(-pay <amount> <user>)\nPays <amount> from your bank account into <user>.",
            "rank": "(-rank [buy] <rank>)\nUsed to buy ranks. If none selected will show the price of the ranks.",
            "daily": "earns you between $20 and $50. Has a 24 hour cooldown.",
            "leaderboard": "Shows the top 5 economy users and your standing. Compiles current value, stock value and rank price",
            "bounty": "Shows current bounties. Do -bounty <bounty name> to see more info and -bounty take <name> to take the bounty",
            "shop": "(-shop or -shop <item>)\nShows the shop and the prices. You can buy items by specifying the item. Item names are case sensitive",
            "inventory": "Shows your owned items",
            "trivia": "Sends a trivia question. You have 10 seconds to send your answer. First person to correctly answer gets 30 to 50 dollars.",
            "stocks": "([buy/sell] <number to buy/sell or 'all'>) \nRunning without args shows the current stock price. Selling or buying's cost is dependant on the current price of stocks"},
        "Other": {
            "bottomgear": "Prints out a randomly generated bottomgear meme. Probably NSFW.",
            "search": "Does a google search for something. Needs rank Gold or above to use.",
            "image": "Does a google image search for something. Needs rank Gold or above to use.",
            "cf": "does a coin flip",
            "ru": "will translate something into russian",
            "info": "prints info about the bot",
            "bb": "calls the AI chatbot to respond to what you said. Is very buggy and slow. Please don't spam it. If it is too slow, feel free to donate $5 to speed it up. You also need rank silver or above for it.",
            "rewind": "(-rewind <number>) \nPrints the most recent mention of anyone in the server and what was said. Goes back <number> mentions",
            "duck": "duck",
            "bucketlist": "prints a to-do list",
            "trans": "prints out the bot's opinion on trans people",
            "ping": "works out the bot's ping",
            "invite": "gets a link for the server and an invite link for the bot",
            "servers": "Shows how many servers the bot is in",
            "code": "gets the link for the github so you can see what goes on under the hood",
            "init": "Sets up the database for the server. It's a good idea to run this whenever the owner or name changes. Also run this if you have not seen this command before.",
            "pussy": "gets an image of some sweet pussy",
            "fox": "Foxes are hella cute",
            "dog": "Dog",
            "mod": "(-mod <name> <on/off>)\nAllows admins to enable and disable some parts of the bot. You will need to run -init for it to work"}
    }
    return helper
