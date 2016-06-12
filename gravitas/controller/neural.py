"""A player controller that uses a neural network to determine the next move"""

from .random import RandomAI_PC

import tensorflow as tf
class Neurotic_PC(RandomAI_PC):
    """We extend the random AI so that we don't have to implement everything"""
    def __init__(self, player, args,container):
        super().__init__(player,args, container)
        self.playNetwork = None

    def pollPlay(self, state):
        if self.playNetwork is None:
            raise ValueError("Please initialize the playnetwork "+
                             "(use neurotic factory)")
        hand = self.player.getHand()
        enemies = [x for x in state.players.values() if x.ship != self.player]
        hulks = list(state.hulks.values())
        feed_dict = {
            "player_position:0": self.player.getPos(),
            "enemy_position_0:0":enemies[0].ship.getPos(),
            "enemy_position_1:0":enemies[1].ship.getPos(),
            "enemy_position_2:0":enemies[2].ship.getPos(),
            "hulk_position_0:0":hulks[0].ship.getPos(),
            "hulk_position_1:0":hulks[1].ship.getPos(),
        }
        for (i,card) in enumerate(hand):
            feed_dict["card_%i_value:0" % i] = card.getValue()
            feed_dict["card_%i_effect:0" % i] = card.getType()
            feed_dict["card_%i_play_order:0" % i] = ord(card.getName()[0])
        with self.playNetwork.graph.as_default():
            with tf.Session() as sess:
                prefrences = enumerate(sess.run(self.playNetwork.tensor, feed_dict=feed_dict))
                from operator import itemgetter
                prefrences = sorted(prefrences, key=itemgetter(1), reverse=True)
                for (prefIndex, prefScore)in prefrences:
                    if prefIndex < len(hand):
                        self.log.debug("neurotic played %i with score %.2f" % (prefIndex, prefScore))
                        return hand[prefIndex]
        raise RuntimeError("Neural network failed, we shouldn't reach here")

from collections import namedtuple

# To prevent cycles, we use layers, inputs can only come from layers before
# the current operation
Position=namedtuple('Position', ['layer', 'index'])

class Node:
    """Mutable structure for creating the neural network
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
        return self.createEagerly(nodeDict)

    def createEagerly(self,nodeDict):
        """Allows the actual constrution to be overwritten"""
        inputTensors = [nodeDict[p].createTensor(nodeDict) for p in self.inputs]
        self.tensor = self.operation(*inputTensors)
        return self.tensor

class InputNode(Node):
    """An input node requires a little more information than a regular node
    A name is required for example, also the tensor construction is quite
    different
    """
    def __init__(self, name):
        self.value = None
        self.name = name
        super().__init__()
    def createEagerly(self,nodeDict):
        self.tensor = tf.placeholder(
            tf.int32,
            shape=[],
            name=self.name
        ) if self.value is None else tf.placeholder_with_default(
            tf.constant(self.value),
            shape=[],
            name=self.name
        )
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
        self.layerDepth = Builder.inputlayer + 1

    def clearTensors(self):
        """Usefull for exporting, tensors are lazily loaded anyway"""
        for key, value in self.nodes.items():
            if not isinstance(value, int):
                value.tensor = None
        return self

    def use(self, other):
        """Tell this builder to use this existing structure"""
        import copy
        for key, value in other.nodes.items():
            if isinstance(value, int):
                self.nodes[key] = value
            else:
                value.tensor = None
                self.nodes[key] =copy.deepcopy(value)
        # can be shallow because tupples are immutable
        self.outputs = copy.copy(other.outputs) 
        self.layerDepth = other.layerDepth
        return self

    def addInput(self, name, value=None):
        """Add an placeholder tensor to the inputlayer"""
        result = InputNode(name)
        result.value = value
        inputCount = self.getNodeCountFor(Builder.inputlayer)
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

    def createGraph(self):
        """Creates the output tensor which is a preference list,
        """
        graph = tf.Graph()
        tensor = None
        with graph.as_default():
            # first make sure all input exists (otherwise tf will complain)
            for i in range(0,self.getNodeCountFor(self.inputlayer)):
                self.nodes[Position(layer=self.inputlayer, index=i)].createTensor(
                    self.nodes
                )
            # to create we just go back over the network
            tensor = tf.pack(
                [self.nodes[x].createTensor(self.nodes) for x in self.outputs]
            )
        graph.finalize()
        TFlow=namedtuple('TFlow', ['graph', 'tensor'])
        return TFlow(graph, tensor)

class Strain:
    """
    A strain in the neuro evolution stack.

    We want to do extra PC configuration, to do this we create a functor
    that receives the builder with the network configuration
    But if the PC hasn't changed since last run we can just reuse it.
    """
    def __init__(self, builder):
        self.builder = builder
        self.lazyPC = None
        self.score = -1

    def createFSNeat():
        """Creates a sparsely connected neurotic factory"""
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
            builder.outputs.append(
                Position(
                    Builder.inputlayer,
                    inputs.pop(
                        random.randrange(len(inputs))
                    )
                )
            )
        return Strain(builder)

    def createNeuroticPC(self, player, args, container):
        """Attach this instead of the default init"""
        if not self.lazyPC:
            self.lazyPC = Neurotic_PC(player, args, container)
            self.lazyPC.playNetwork = self.builder.createGraph()
        else:
            # bypass creation if we already have the lazy value
            nw = self.lazyPC.playNetwork
            self.lazyPC.__init__(player,args,container)
            self.lazyPC.playNetwork = nw
        return self.lazyPC 

    # classes are more like functions in python anyway
    Operation=namedtuple('Operation', ['function', 'argcount'])
    operations = [
        # functions are more like arguments in python anyway
        Operation(tf.add, 2),
        Operation(tf.sub, 2),
        Operation(tf.mul, 2),
        Operation(tf.floordiv, 2),
        Operation(tf.mod, 2),
        Operation(tf.neg, 1),
    ]
    def mutate(self):
        import random
        # select layer to modify
        layer = random.randrange(self.builder.inputlayer+1, self.builder.layerDepth+1)
        # the position for the new node
        position = Position(layer, self.builder.getNodeCountFor(layer))
        # select an operation
        operation = random.choice(self.operations)
        # select the inputs
        inputs = []
        # prefer replacing an existing output as input
        availableOutputs = [o for o in self.builder.outputs if o.layer < layer]
        print("available %i, layer: %i" % (len(availableOutputs), layer))
        if len(availableOutputs) > 0:
            index = random.randrange(len(availableOutputs))
            inputs.append(availableOutputs[index])
            self.builder.outputs[index] = position

        while len(inputs) < operation.argcount:
            layer = random.randrange(self.builder.layerDepth)
            inputs.append(Position(
                layer,
                random.randrange(self.builder.getNodeCountFor(layer))
            ))
        # add the operation
        self.builder.addOpperation(operation.function, position, inputs)
        return self
