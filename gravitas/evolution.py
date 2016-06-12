#!/usr/bin/env python
"""
peform neuro-evolution
"""
import main
import json
from factory import Factory
from controller.neural import Neurotic_PC, NeuroticFactory
class config:
    controller = "neuroticAI"
    player = "Darwin"
    runs = 10
    significantDifference = 0.05


neuroticFactory = NeuroticFactory.createFSNeatFactory()
def compete(NeuroticFactory, config):
    args = main.parser.parse_args(['-c', 'conf/neurotic.json', '--headless', '-l', '0'])
    factory = Factory(args)
    factory.controllerTypes[config.controller] = neuroticFactory.createNeuroticPC
    result = []
    for run in range(0, config.runs):
        print("run %i" %  run)
        runsult = main.run(factory)
        print(runsult)
        result.append([pl[1] for pl in runsult if pl[0] == config.player][0])
    return result

print(compete(neuroticFactory, config))

