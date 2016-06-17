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
    controller = "neuroticAI"
    player = "Darwin"
    runs = 4 # scoring runs, result of findnum.py
    generations = 2 # evolution cycles
    significantDifference = 0.05
    popsize = 8
    jsonfile = 'conf/neurotic2p.json'
    enemyCount = 1
    hulkCount = 1
    filename = "evolution.pikl"

def compete(arg):
    (strain, config) = arg
    args = main.parser.parse_args(['-c', config.jsonfile, '--headless', '-l', '0'])
    factory = Factory(args)
    factory.controllerTypes[config.controller] = strain.createNeuroticPC
    result = []
    for _ in range(0, config.runs):
        runsult = main.run(factory)
        result.append([pl[1] for pl in runsult if pl[0] == config.player][0])
    return result

from multiprocessing import Pool
pool = Pool(config.workerProcesses) # sub interpreters to use
def evaluateGeneration(members):
    # calculating the results is a lot of work, lets not do it ourselves,
    # but use a process worker pool instead
    results = pool.map( # use the pool
        compete, # function to be used
        zip( # dirty ack to pass multiple arguments
            members,
            [config for _ in range(0,len(members))]
        )
    )
    for (member,scores) in zip(members,results):
        member.score = sum(scores)/len(scores)

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
population = loadEvolution() if isfile(config.filename) else [
    Strain.createFSNeat(config.enemyCount, config.hulkCount) for _ in range(0,config.popsize)
]

evaluateGeneration(population)

def printpop(population):
    print("current pop: [%s]" % ', '.join(['%.2f' % pop.score for pop in population]))

for generation in range(0,config.generations):
    print("generation %i" % generation)
    printpop(population)

    children = [Strain(Builder().use(pa.builder)) for pa in population]
    for child in children:
        child.mutate()

    evaluateGeneration(children)

    for child in children:
        print(json.dumps({"s":child.score, "outs":child.builder.outputs}))
    population = selection(population, children)

printpop(population)

with open(config.filename, 'wb') as pickleFile:
    pickle.dump({'population': population, 'generation':generation+1}, pickleFile)
