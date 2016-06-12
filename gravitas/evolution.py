#!/usr/bin/env python
"""
peform neuro-evolution
"""
import main
import json
from factory import Factory
from controller.neural import Neurotic_PC, Strain, Builder
class config:
    controller = "neuroticAI"
    player = "Darwin"
    runs = 3 # scoring runs, result of findnum.py
    generations = 5 # evolution cycles
    significantDifference = 0.05
    popsize = 2


def compete(strain, config):
    args = main.parser.parse_args(['-c', 'conf/neurotic.json', '--headless', '-l', '0'])
    factory = Factory(args)
    factory.controllerTypes[config.controller] = strain.createNeuroticPC
    result = []
    for run in range(0, config.runs):
        print("run %i" %  run)
        runsult = main.run(factory)
        result.append([pl[1] for pl in runsult if pl[0] == config.player][0])
    return result

def evaluateGeneration(members):
    for member in members:
        member.mutate()
        scores = compete(member, config)
        member.score = sum(scores)/len(scores)

import random
def selection(parents, children):
    random.shuffle(children)
    # make a tupple with zip and then compare, this is tournament selection
    return [p if p.score > c.score else c for (p, c) in zip(parents,children)]
population = [Strain.createFSNeat() for _ in range(0,config.popsize)]

evaluateGeneration(population)

def printpop(population):
    print("current pop: [%s]" % ', '.join(['%.2f' % pop.score for pop in population]))
for generation in range(0,config.generations):
    print("generation %i" % generation)
    printpop(population)
    children = [Strain(Builder().use(pa.builder)) for pa in population]
    evaluateGeneration(children)
    population = selection(population, children)


printpop(population)
