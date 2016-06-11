#!/usr/bin/env python
"""
peform neuro-evolution
"""
import main
import json
from factory import Factory
from controller.neural import Neurotic_PC, NeuroticFactory

args = main.parser.parse_args(['-c', 'conf/neurotic.json', '--headless', '-l', '0'])

neuroticFactory = NeuroticFactory.createFSNeatFactory()
factory = Factory(args)
factory.controllerTypes["neuroticAI"] = neuroticFactory.createNeuroticPC

result = main.run(factory)

print(result)
playerCount = len(factory.createState().players)

