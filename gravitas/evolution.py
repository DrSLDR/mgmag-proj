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
    runs = 10 # scoring runs, result of findnum.py
    generations = 10 # evolution cycles
    significantDifference = 0.05
    popsize = 8

def compete(arg):
    (strain, config) = arg
    args = main.parser.parse_args(['-c', 'conf/neurotic.json', '--headless', '-l', '0'])
    factory = Factory(args)
    factory.controllerTypes[config.controller] = strain.createNeuroticPC
    result = []
    for _ in range(0, config.runs):
        runsult = main.run(factory)
        result.append([pl[1] for pl in runsult if pl[0] == config.player][0])
    return result

from multiprocessing import Pool
pool = Pool(config.workerProcesses)
def evaluateGeneration(members):
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
    for child in children:
        child.mutate()
        print(json.dumps(child.builder.outputs))

    evaluateGeneration(children)
    population = selection(population, children)


printpop(population)

import json
from json import JSONEncoder
class DictEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Builder) or isinstance(obj, Node):
            return obj.__dict__
        if isinstance(obj, set):
            return list(obj)
        import tensorflow as tf
        if tf.add == obj or tf.neg == obj or tf.sub == obj or tf.mul == obj:
            return obj.__name__
        return super().default(obj)

for member in population:
    builder = member.builder
    builder.clearTensors()
    for key in dict(builder.nodes).keys():
        builder.nodes[str(key)] =builder.nodes[key]
        del builder.nodes[key]

    import pprint
    print(json.dumps(builder, cls=DictEncoder))
