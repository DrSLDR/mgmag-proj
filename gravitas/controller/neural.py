"""A player controller that uses a neural network to determine the next move"""

from .random import RandomAI_PC

import tensorflow as tf
class Neurotic_PC(RandomAI_PC):
    """We extend the random AI so that we don't have to implement everything"""
    def __init__(self, player, args,container):
        super().__init__(player,args, container)
        self.playNetwork = Factory.createPlay()

    def pollPlay(self, state):
        hand = self.player.getHand()
        enemies = [x for x in state.players if x[0] != self.player]
        feed_dict = {
            "player_position:0": self.player.getPos(),
            "enemy_position_0:0":enemies[0][0].getPos(),
            "enemy_position_1:0":enemies[1][0].getPos(),
            "enemy_position_2:0":enemies[2][0].getPos(),
            "hulk_position_0:0":state.hulks[0][0].getPos(),
            "hulk_position_1:0":state.hulks[1][0].getPos(),
        }
        for (i,card) in enumerate(hand):
            feed_dict["card_%i_value:0" % i] = card.getValue()
            feed_dict["card_%i_effect:0" % i] = card.getType()
            feed_dict["card_%i_play_order:0" % i] = ord(card.getName()[0])
        import pprint
        pprint.PrettyPrinter(indent=4).pprint(feed_dict)
        with tf.Session() as sess:
            prefrences = enumerate(sess.run(self.playNetwork, feed_dict=feed_dict))
            from operator import itemgetter
            prefrences = list(sorted(prefrences, key=itemgetter(1), reverse=True))
            for (prefIndex, prefScore)in prefrences:
                if prefIndex < len(hand):
                    print("neurotic played %i with score %.2f" % (prefIndex, prefScore))
                    return hand[prefIndex]
            print(prefrences)
        raise RuntimeError("Neural network failed, we shouldn't reach here")

from collections import namedtuple

InputNode=namedtuple('InputNode', ['name', 'default_value'])
Operation=namedtuple('Operation', [
    'tensorFunction',
    # where inputs are prerably the inputtupple type in a list
    'arguments'
])
# where source is a member of te Sources tupple, and index just an int
# cannot go forward in the indeci, only backward (in case of the operations)
Input=namedtuple('Input', ['source', 'index'])
from enum import Enum
Sources = Enum('Sources', 'input operation')

class Builder:
    """The tensorflow neuralnetworks are immutable, this means we need
    to define a structure around it to do neuro evolution (since we want
    to change the graph)

    For all uninitialized, a tensor is a result of an operation.
    See it as a datapipe, we predifine a set of tensors 
    (so a network of "pipes"), placeholders are used to determine where input
    should go. So we first create the computation network (with help of
    this class), and later we use this network to figure out what to do.
    """

    def __init__(self):
        self.inputNodes = [] # list of inputnodes
        self.operationNodes = [] # list of operations
        self.outputNodes = [] # list of inputs (I mean the namedtuple)

    def addInput(self, name, value=None):
        self.inputNodes.append(InputNode(name=name, default_value=value))

    def addOpperation(self, function, arguments):
        self.operationNodes.append(Operation(function, arguments))
    def _inputTuppleToTensor(tupple):
        if tupple.default_value is None:
            return tf.placeholder(tf.int32, shape=[], name=tupple.name)
        return tf.placeholder_with_default(
            tf.constant(tupple.default_value), shape=[], name=tupple.name
        )

    def createOutputTensor(self):
        """Creates the output tensor which is a preference list,

        Goes trough the input nodes first to create tensors from them,
        then defines the resolve function which can resolve the input tupple
        (ie another tensor), from there the operations are build one by one.

        after that the output nodes are build and finally put into a pack
        tensor. Using a pack tensor allows us to execute just this tensor
        rather than calling the neural network multiple times
        """
        # to create we just go back over the network
        inputTensors = list(
            map(Builder._inputTuppleToTensor, self.inputNodes)
        )
        operationTensors = []
        tensors = {
            Sources.input: inputTensors,
            Sources.operation: operationTensors
        }
        def resolveInput(nput): # input is a keyword
            return tensors[nput.source][nput.index]
        for operation in self.operationNodes:
            operationTensors.append(
                operation.tensorFunction(
                    # the star makes from the list arguments
                    *[resolveInput(i) for i in operation.arguments]
                )
            )
        return tf.pack([resolveInput(x) for x in self.outputNodes])

class Factory:
    def createPlay():
        """Creates a sparsely connected play network"""
        builder = Builder()
        for i in range(0,8):
            builder.addInput("card_%i_value" % i, 1)
            builder.addInput("card_%i_effect" % i, 0)
            builder.addInput("card_%i_play_order" % i, 0)
        builder.addInput("player_position")
        for i in range(0,3):
            builder.addInput("enemy_position_%i" % i)
        for i in range(0,2):
            builder.addInput("hulk_position_%i" % i)
        for i in range(0,8):
            builder.outputNodes.append(Input(Sources.input, i))
        builder.addOpperation(tf.add, [
                Input(Sources.input, 3),
                Input(Sources.input, len(builder.inputNodes)-1)
            ]
        )
        builder.outputNodes[3] = Input(Sources.operation, 0)
        return builder.createOutputTensor()
