#!/usr/bin/env python
"""
peform neuro-evolution
"""
import main
import json
import random
import pickle
from os.path import isfile

from factory import Factory
from controller.neural import Neurotic_PC, Strain, Builder, Node

class config:
    """static config"""
    workerProcesses = 8 # match your "thread" count of your cpu for maximum performance
    controller = ["neuroticAI", "neuroticAI2", "neuroticAI3", "neuroticAI4"]
    player = ["Darwin", "Randy", "Squirtle", "Rachel"]
    tournamentSize = 4
    runs = 1180 # scoring runs, result of findnum.py
    generations = 50 # evolution cycles
    significantDifference = 0.025
    popsize = 8
    jsonfile = 'conf/neurotic.json'
    enemyCount = 3
    hulkCount = 2
    filename = "evolution.pikl"
    readfile= False

def compete(arg):
    (strains, config) = arg
    args = main.parser.parse_args(['-c', config.jsonfile, '--headless', '-l', '0'])
    factory = Factory(args)
    for (i, strain) in enumerate(strains):
        factory.controllerTypes[config.controller[i]] = strain.createNeuroticPC
    result = []
    for run in range(0, config.runs):
        runsult = main.run(factory)
        def getPlayerScore(player):
            # extract the score...
            return [pl[1] for pl in runsult if pl[0] == player][0]
        result.append([getPlayerScore(player) for player in config.player])
    return result

from multiprocessing import Pool
pool = Pool(config.workerProcesses) # sub interpreters to use

def evaluateGeneration(parents, *children):
    for childlists in children:
        random.shuffle(childlists) # not always children vs parents, so that strong genes spread
    members = list(zip(parents, *children))
    # calculating the results is a lot of work, lets not do it ourselves,
    # but use a process worker pool instead
    compitionResults = pool.map( # use the pool
        compete, # function to be used
        zip( # dirty ack to pass multiple arguments
            members,
            [config for _ in range(0,len(parents))]
        )
    )
    from collections import namedtuple
    Score = namedtuple('Score', ['member', 'score'])
    results = []
    for (i,scorestruct) in enumerate(compitionResults):
        # zip zop zap!
        # Don't worry, I stack overflowed it, this totally should work they say
        candidates = []
        for (competitor, scores) in zip(members[i], list(zip(*scorestruct))):
            candidates.append(Score(competitor, sum(scores)/len(scores)))
        
        scores = [x.score for x in candidates]
        average = sum(scores)/len(scores)
        best = max(scores)
        fraction = average * config.significantDifference

        # you can be selected if your score diff is smaller than the significant fraction
        # this always includes the best
        filtered = [cand.score for cand in candidates if (cand.score - average) < fraction]
        selected = [cand.score for cand in candidates if (cand.score - average) >= fraction]
        print("selected (count: %i, scores %s), best %.4f, fraction %.4f, un-significant (%s)" % (
            len(selected), json.dumps(selected), best, fraction, json.dumps(filtered)
        ))
        # if we have to select randomly from the candidates, why not just select
        # the best? True he may be just lucky, but we have to choose at this point
        candidates = [cand for cand in candidates if best == cand.score]
        results.append(random.choice(candidates).member)
    return results

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
    print("generation %i" % generation)


    def createChildren():
        children = [Strain(Builder().use(pa.builder)) for pa in population]
        for child in children:
            child.mutate()
        return children

    population = evaluateGeneration(population, *[createChildren() for _ in range(1,config.tournamentSize)])

    for member in population:
        print(json.dumps(member.builder.outputs))
    # just save each generation, so quiting doesn't become so painfull
    with open(config.filename, 'wb') as pickleFile:
        pickle.dump({'population': population, 'generation':generation+1}, pickleFile)
