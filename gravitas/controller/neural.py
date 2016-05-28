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
        self.log.debug(pprint.PrettyPrinter(indent=4).pformat(feed_dict))
        with tf.Session() as sess:
            prefrences = enumerate(sess.run(self.playNetwork, feed_dict=feed_dict))
            from operator import itemgetter
            prefrences = list(sorted(prefrences, key=itemgetter(1), reverse=True))
            for (prefIndex, prefScore)in prefrences:
                if prefIndex < len(hand):
                    self.log.debug("neurotic played %i with score %.2f" % (prefIndex, prefScore))
                    return hand[prefIndex]
            print(prefrences)
        raise RuntimeError("Neural network failed, we shouldn't reach here")

from collections import namedtuple

# To prevent cycles, we use layers, inputs can only come from layers before
# the current operation
Position=namedtuple('Position', ['layer', 'index'])

class Node:
    """Mutable strcuture for creating the neural network
    Each node represents an operation. The first nodes are placeholders
    """
    def __init__(self):
        # list of positions where self.position.layer < input.position.layer
        # ie, we don't want cycles
        self.inputs = [] 
        self.position = Position(0,0)
        # the operation can create a tensor, we want to do this lazily,
        # so we can still "modify" the tensor graph
        self.operation = None
        # The tensor is the end result
        self.tensor = None
        # list of positions that use this node
        # useful to know if we want to delete this node but preserve
        # connections
        self.usedBy = set()

    def createTensor(self, nodeDict):
        """Creates the tensor or returns the current one"""
        if self.tensor is not None:
            return self.tensor
        inputTensors = [nodeDict[p].createTensor(nodeDict) for p in self.inputs]
        self.tensor = self.operation(*inputTensors)
        return self.tensor

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

    inputlayer = 0
    # to track the nodes in a layer (so we can add a new one
    # without overiding a previous
    nodeCountindex = -1 
    def __init__(self):
        self.nodes = dict() # graph dict
        self.outputs = [] # list of positions in the nodes
        self.layerDepth = Builder.inputlayer

    def addInput(self, name, value=None):
        """Add an placeholder tensor to the inputlayer"""
        result = Node()
        result.tensor = tf.placeholder(
            tf.int32,
            shape=[],
            name=name
        ) if value is None else tf.placeholder_with_default(
            tf.constant(value),
            shape=[],
            name=name
        )
        inputCount = self.getNodeCountFor(Builder.inputlayer)
        result.inputs = None
        # inputs are always layer 0
        result.position = Position(Builder.inputlayer,inputCount)
        self.nodes[result.position] = result
        self._increaseNodeCountFor(Builder.inputlayer)

    def _nodeCountPos(layer):
        return Position(layer, Builder.nodeCountindex)
    def getNodeCountFor(self, layer):
        position = Builder._nodeCountPos(layer)
        if position not in self.nodes:
            self.nodes[position] = 0
        return self.nodes[position]
    def _increaseNodeCountFor(self, layer):
        position = Builder._nodeCountPos(layer)
        self.nodes[position] = self.getNodeCountFor(layer) + 1

    def removeOpperation(self, position):
        inputs = self.nodes[position].inputs
        if not inputs:
            raise ValueError("Trying to remove inputnode")
        for user in self.nodes[position].usedBy:
            # remove from the graph by saying it no longer exists
            user.inputs -= position
            # the paper sais we should try and link trough the arguments
            # because removing completly is to destructive
            user.inputs += inputs[0]
        del self.nodes[position]
        
    def addOpperation(self, function, position, arguments):
        if position in self.nodes:
            raise ValueError("Do what? replace it?")
        for argument in arguments:
            if argument.layer >= position.layer:
                raise ValueError(("To prevent cycles, arguments should always "+
                                 "come from earlier layers. Argument: %s, "+
                                 "Operation position %s") % (argument, position))
            self.nodes[argument].usedBy.add(position)
        result = Node()
        result.operation = function
        result.position = position
        result.inputs = arguments
        self.nodes[position] = result
        self._increaseNodeCountFor(position.layer)
        if position.layer > self.layerDepth:
            self.layerDepth = position.layer

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
        return tf.pack(
            [self.nodes[x].createTensor(self.nodes) for x in self.outputs]
        )

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
        import random
        inputs = list(range(0, builder.getNodeCountFor(Builder.inputlayer)))
        for i in range(0,8):
            builder.outputs.append(Position(Builder.inputlayer, inputs.pop(random.randrange(len(inputs)))))
        pos = Position(1, builder.getNodeCountFor(builder.layerDepth))
        builder.addOpperation(tf.add, pos, [Position(Builder.inputlayer, 1), Position(Builder.inputlayer, 3)])
        builder.outputs[3] = pos
        return builder.createOutputTensor()
