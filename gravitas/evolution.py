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
    player = ["Darwin"]
    tournamentSize = 4
    runs = 100 # scoring runs, result of findnum.py
    generations = 50 # evolution cycles
    significantDifference = 0.025
    popsize = 8
    jsonfile = 'conf/neurotic.json'
    enemyCount = 3
    hulkCount = 2
    filename = "evolution.pikl"
    readfile= False

def compete(arg):
    (strains, config, seed) = arg
    print("seed: %s", seed)
    rng = random.Random()
    rng.seed(seed)
    args = main.parser.parse_args(['-c', config.jsonfile, '--headless', '-l', '0'])
    factory = Factory(args)
    factory.rng.seed(rng.randrange(maxsize))
    for (i, strain) in enumerate(strains):
        print("nr: %i, strain: %s" % (i,type(strain).__name__))
        factory.controllerTypes[config.controller[i]] = strain.createNeuroticPC
    result = []
    for run in range(0, config.runs):
        randone = factory.rng.randrange(500)
        runsult = main.run(factory)
        print("run %i, game id %i, and %i" % (run, randone, factory.rng.randrange(500)))
        def getPlayerScore(player):
            # extract the score...
            return [pl[1] for pl in runsult if pl[0] == player][0]
        result.append([getPlayerScore(player) for player in config.player])
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
    results = []
    for (i,scorestruct) in enumerate(zip(members, compitionResults)):
        candidates = []

        # we have 2 lists [member1, member2] with the members
        # and another [[score1, score2], [score3, score4]]
        # now we want to all scores in index 1 to member1 and so on...
        # so the result is [(member1, [score1, score3]), (member2, [score2, score4])]
        # turns out you can do this with zip and zip*.
        labeledScores = zip(members[i], list(zip(*scorestruct)))
        for (competitor, scores) in labeledScores:
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
