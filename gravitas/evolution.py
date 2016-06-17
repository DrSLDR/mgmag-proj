#!/usr/bin/env python
"""
peform neuro-evolution
"""
import main
import json
from factory import Factory
from controller.neural import Neurotic_PC, Strain, Builder, Node
class config:
    workerProcesses = 8 # match your "thread" count of your cpu for maximum performance
    controller = ["neuroticAI", "neuroticAI2"]
    player = ["Darwin", "Randy"]
    runs = 60 # scoring runs, result of findnum.py
    generations = 50 # evolution cycles
    significantDifference = 0.05
    popsize = 8
    jsonfile = 'conf/neurotic2p.json'
    enemyCount = 1
    hulkCount = 1
    filename = "evolution.pikl"
    readfile= False

def compete(arg):
    (strains, config) = arg
    args = main.parser.parse_args(['-c', config.jsonfile, '--headless', '-l', '0'])
    factory = Factory(args)
    for (i, strain) in enumerate(strains):
        factory.controllerTypes[config.controller[i]] = strain.createNeuroticPC
    result = []
    for _ in range(0, config.runs):
        runsult = main.run(factory)
        def getPlayerScore(player):
            # extract the score...
            return [pl[1] for pl in runsult if pl[0] == player][0]
        result.append([getPlayerScore(player) for player in config.player])
    return result

from multiprocessing import Pool
pool = Pool(config.workerProcesses) # sub interpreters to use

def evaluateGeneration(parents, children):
    random.shuffle(children) # not always children vs parents, so that strong genes spread
    members = list(zip(parents, children))
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
        candidates = [cand for cand in candidates if (cand.score - best) < fraction]
        print("candidates scores %s with best %.4f" % (json.dumps([c.score for c in candidates]), best))
        results.append(random.choice(candidates).member)
    return results

import random
def selection(parents, children):
    def select(parent, child):
        avg = (parent.score + child.score) / 2
        fraction = avg * config.significantDifference
        if abs(parent.score - child.score) < fraction:
            print("difference between (p %.2f, c %.2f) smaller then %.2f, returning randomly" %
                  (parent.score, child.score, fraction)
            )
            return random.choice([parent,child])
        return parent if parent.score > child.score else child

    random.shuffle(children)
    # make a tupple with zip and then compare, this is tournament selection
    return [select(p,c) for (p, c) in zip(parents,children)]

from os.path import isfile
import pickle
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

    children = [Strain(Builder().use(pa.builder)) for pa in population]
    for child in children:
        child.mutate()

    population = evaluateGeneration(population, children)

    for member in population:
        print(json.dumps(member.builder.outputs))

with open(config.filename, 'wb') as pickleFile:
    pickle.dump({'population': population, 'generation':generation+1}, pickleFile)
