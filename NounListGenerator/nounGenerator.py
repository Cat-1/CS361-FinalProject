import yaml, random

try:
    from yaml import CLoader as loader, CDumper as dumper
except ImportError:
    from yaml import loader, dumper
stream = open("config.yaml")
config = yaml.load(stream, loader)
random.seed()


def get_random_word(wordList, size):
    index = random.randint(0, size - 1)
    word = wordList[index]
    wordList.pop(index)
    return word

array = []
with open(config["input"]["path"],"r") as f:
    contents = f.readlines()
    [array.append(row) for row in contents]

    numWords = int(config["input"]["numNouns"])

    with open(config["output"]["path"], "w") as outfile:
        for i in range(0,numWords):
            word = get_random_word(array, len(array))
            outfile.write(word)
