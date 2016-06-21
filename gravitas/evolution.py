#!/usr/bin/env python
"""
peform neuro-evolution
"""
import main
import json
import random
import pickle
from sys import maxsize
from os.path import isfile

from factory import Factory
from controller.neural import Neurotic_PC, Strain, Builder, Node

class config:
    """static config"""
    workerProcesses = 8 # match your "thread" count of your cpu for maximum performance
    controller = ["neuroticAI"]
    player = "Darwin" # the AI slot to train, should match the config file
    offspringCount = 1
    runs = 20 # scoring runs, result of findnum.py
    countIncrease = 4 # if an AI beats 50% of the time, how much to increase
    generations = 400 # evolution cycles
    popsize = 16
    jsonfile = 'conf/neurotic.json'
    enemyCount = 3
    hulkCount = 2
    filename = "evolution.pikl"
    readfile= False

def compete(arg):
    (strains, config, seed) = arg
    rng = random.Random()
    rng.seed(seed)
    args = main.parser.parse_args(['-c', config.jsonfile, '--headless', '-l', '0'])
    factory = Factory(args)
    factory.rng.seed(rng.randrange(maxsize))
    for (i, strain) in enumerate(strains):
        factory.controllerTypes[config.controller[i]] = strain.createNeuroticPC
    result = []
    for run in range(0, config.runs):
        randone = factory.rng.randrange(500)
        runsult = main.run(factory)
        result.append(runsult)
    return result

from multiprocessing import Pool
pool = Pool(config.workerProcesses) # sub interpreters to use

def evaluateGeneration(parents, *children):
    members = list(parents)
    for mutations in children:
        members.extend(mutations)
    members = [[x] for x in members]
    generationSeed = random.randrange(maxsize)
    # calculating the results is a lot of work, lets not do it ourselves,
    # but use a process worker pool instead
    def foreachMember(value):
        return [value for _ in range(0,len(members))]
    compitionResults = pool.map( # use the pool
        compete, # function to be used
        zip( # dirty ack to pass multiple arguments
            members,
            foreachMember(config),
            foreachMember(generationSeed)
        )
    )
    from collections import namedtuple
    Score = namedtuple('Score', ['member', 'score'])

    def countWins(scores):
        wins = 0
        for score in scores:
            if sorted(score, key = lambda x: x[1])[-1][0] == config.player:
                wins += 1
        return wins
    results = [Score(member[0], countWins(scores)) for (member,scores) in zip(members, compitionResults)]
    sortedResutls = sorted(results, key=lambda x: x.score)
    bestScore = sortedResutls[-1].score
    if bestScore > config.runs * 0.5:
        config.runs += 4
        print("increasing runcount to %i an AI beat half of the runs with score: %i" % (config.runs, bestScore))
    return [element.member for element in sortedResutls][-config.popsize:]

def loadEvolution():
    with open(config.filename, 'rb') as pickleFile:
        print("loading %s" % config.filename)
        result = pickle.load(pickleFile)
        print("loaded population at generation %i" % result['generation'])
        return result['population']
population = loadEvolution() if config.readfile and isfile(config.filename) else [
    Strain.createFSNeat(config.enemyCount, config.hulkCount) for _ in range(0,config.popsize)
]

for generation in range(0,config.generations):
    print("generation %i, runcount: %i" % (generation, config.runs))

    def createChildren():
        children = [Strain(Builder().use(pa.builder)) for pa in population]
        for child in children:
            child.mutate()
        return children

    population = evaluateGeneration(population, *[createChildren() for _ in range(0,config.offspringCount)])

    for member in population:
        print(json.dumps(member.builder.outputs))
    # just save each generation, so quiting doesn't become so painfull
    with open(config.filename, 'wb') as pickleFile:
        pickle.dump({'population': population, 'generation':generation+1}, pickleFile)
