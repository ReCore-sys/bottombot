import random


def bottomchoice():
    verb1 = random.choice(["fucking ends", "voilently penetrates", "gives a hicky to", "stabs", "reinvents", "violates", "scams",
                          "sells ketamine to", "buys ketamine from", "drives over", "has an unusually vigorous orgy with", "unhinges his jaw and devours"])
    noun1 = random.choice(["god", "your mother", "pyro from tf2", "the Queen", "a 1982 Rolls Royce Silver Wraith", "the 1999 toyota corolla", "Lebron James",
                          "a 100% legitimate nigerian prince", "253 primary school students", "the entirety of europe", "the abstract concept of time", "a male stripper"])
    verb2 = random.choice(["bash", "assimilate", "make explosive love to", "commit crimes to", "alt-f4", "give heroin to",
                          "start a crack epidemic with", "whisper seductively to", "bully", "drink", "start a pyramid scheme with", "time travels"])
    noun2 = random.choice(["dwane the cock jhonson", "5th grade stoners", "ben shapiro", "Mike Oxlong", "you",
                          "Jehova", "Heavy", "[Redacted]", "Ugandan villagers", "the middle east", "Jimmy Neutron", "toaster", "crack"])
    verb3 = random.choice(["jacks off", "uninstalls", "eviscerates", "obliterates", "assults", "finds the secret cross-dressing wardrobe of",
                          "speed-dates", "invests in bitcoin with", "falls in love with", "dismantles", "severely irradiates", "sensually kisses"])
    noun3 = random.choice(["my dick", "Satan", "the Syrian schoolhouse", "your future kids", "a Tsar Bomba", "the Gustav Railway Gun", "Zimbabwe", "Mark Zuckerberg", "Jeff Bezos", "Uncle Sam", "The Chinese Communist Party", "Great Leader Kim Jong Un, wise and just ruler of The Democratic People's Republic of North Korea, greatest nation of all time",
                          "an A-10 warthog", "the Lockheed-Martin company", "the exhaust pipe of a Western Star cargo truck", "a BMW motorbike", "an electric car", "7 metric tonnes of raw plutonium ore", "2 crates of C4", "an entire keg of beer", "a quaint village bakery in western France", "an elderly gardener", "Donald J Trump", "Bernie Sanders", "Stalin", "a duck"])
    consequence = random.choice(["deeply regrets it", "gets a huge boner from it", "is anointed Grand High Emperor", "is promptly arrested", "gets sent to a gulag", "gets stabbed", "is tried for war crimes", "is found innocent", "receives a life sentence", "gets addicted",
                                "is nominated for a Nobel Peace Prize", "is violently and lovingly dismembered", "is turned inside out", "gets to meet the man of his dreams", "loses in monopoly", "is forced to step on lego", "gets glenysed", "is made to program in R", "very minor case of serious brain damage"])

    james = random.choice(
        ["James", "James", "james", "jmaes", "janes", "Jams"])
    hammond = random.choice(
        ["Hammond", "Hammond", "hammond", "ham", "hamoc", "Hamnd", "hmalet", "hampomd"])

    # this compiles a random choice from each list into one large string. Feel free to add stuff to the list.
    output = f"Tonight on bottomgear {james} {verb1} {noun1}, I {verb2} {noun2} and {hammond} {verb3} {noun3} and {consequence}"
    return str(output)
