"""A player controller that uses a neural network to determine the next move"""

import tensorflow as tf

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

# Considered architectures:
# 1. a matrix of inputs, the problem was that you cannot get a reduced value,
# reliably out of this with random modiification to the graph
# 2. All integer inputs, this is the one I went for
#     1. A single output node that did some summing and then use a modulo to
#        figure out which card, the problem is that a modulo is extremly complex
#     2. Preference based output, each card gets a output node which determines,
#        Its preference. I like this better
# Then I also considered dropping the resolution order and sorting the cards
# before hand, I chose not to do this, because it relies to much on the
# semantics of the network, I don't know how important resolution order is.
# But I may come back on this one.
#
# The final argument will be a pack command, which jams all output nodes in an
# array so the network only has to consulted once.

class NeuralNetwork:
    def createPlay():
        builder = NeuralNetworkBuilder()
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
        builder.operationNodes.append(Operation(
                tensorFunction=tf.add,
                arguments=[
                    Input(Sources.input, 3),
                    Input(Sources.input, len(builder.inputNodes)-1)
                ]
        ))
        builder.outputNodes[3] = Input(Sources.operation, 0)
        return builder.createOutputTensor()

    def cardToTupple(card):
        from collections import namedtuple
        Card=namedtupple('Card', ['type, value, name'])
        return Card(type=card.getType(), value=card.getValue(),
                    # we need to have the same name datatype,
                    # only the first letter decides the order, we don't care
                    # about the value since it won't matter for the neural
                    # network (it only matters that the values are different)
                    name=ord(card.getName()[0]) 
                    )

    def process(self, cards):
        """
        Use the neural network to proccess the gamestate/mode.
        In the gamestate and mode (ie pollrequest number)
        Out the choice (a number)
        """
        #TODO
        # 1. creation and proccing sperate
        # 2. Sort cards on play order
        cards = map(NeuralNetwork.cardToTupple,cards)
        #values = list(map(lambda x: ,reduce(list.__add__,cards)))


def run():
    with tf.Session() as sess:
        work = NeuralNetwork.createPlay()
        print(sess.run(work, feed_dict={
            "player_position:0": 3,
            "enemy_position_0:0":10,
            "enemy_position_1:0":10,
            "enemy_position_2:0":10,
            "hulk_position_0:0":10,
            "hulk_position_1:0":10,
        }))


class NeuralNetworkBuilder:
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

    def _inputTuppleToTensor(tupple):
        if tupple.default_value is None:
            return tf.placeholder(tf.int32, shape=[], name=tupple.name)
        return tf.placeholder_with_default(
            tf.constant(tupple.default_value), shape=[], name=tupple.name
        )

    def createOutputTensor(self):
        """Creates the neural network based on the configured processing steps"""
        # to create we just go back over the network
        inputTensors = list(
            map(NeuralNetworkBuilder._inputTuppleToTensor, self.inputNodes)
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
