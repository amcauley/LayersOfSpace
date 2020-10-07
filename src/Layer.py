'''
    The Layer class is an abstraction of basically any object ("Item", to avoid confusion with OOO coding terminology).
    It can be owned by parent Layers and own a collection of sub-Layers.
    At its heart, its job is to handle incoming messages by either processing them or routing them to another layer.
'''

from . import Message, Scheduler
from .Log import Log

class Layer:
    def __init__(self, id):
        # Id holds the unique identifier string for this instance.
        self.id = id

        # Tracks upcoming events that this layer needs to know about.
        self.scheduler = Scheduler.Scheduler()

        # Map message type -> handlers this layer will use for its own processing.
        self.handlers = {}

        # Map message type -> sub layers registered to process them.
        self.registrations = {}

        # Layers that list this one as a sub-layer.
        self.parents = []

    def AddMessage(self, ts, message):
        '''
            Add a message into the scheduler at the provided timestamp (ts).
        '''
        self.scheduler.Add(ts, message)

    def AddMessageToItem(self, ts, message, id):
        '''
            Send a message to a specific Item (specified by id), either higher or lower than the current layer.
        '''
        pass

    def AddMessageToItemRelative(self, ts, message, delta):
        '''
            Send a message to 1+ Items above (or below) this one.
                The delta specifies how many Layers to traverse before adding the item.
                Positive = sub layers, Negative = parents.
                If multiple sub/parent layers exist, the message will be added to all of them.
        '''
        pass

    def AddParent(self, parentLayer):
        if parentLayer not in self.parents:
            self.parents.append(parentLayer)

    def GetMessageTypes(self):
        '''
            Returns a set of message types handled by this sub-layer instance.
                This is per-instance and includes any types registered to this particular instance.
        '''
        return set(self.handlers.keys()).union(set(self.registrations.keys()))

    def RegisterSubLayer(self, subLayer):
        '''
            (Re-)Register a sub-layer, i.e. identify which message types it will handle.
        '''
        Log.debug(f'Layer {self} registering subLayer {subLayer}')
        types = self.GetMessageTypes()
        subTypes = subLayer.GetMessageTypes() 

        for type in types:
            if type not in self.registrations:
                self.registrations[type] = []
            self.registrations[type].append(subLayer)

        newTypes = subTypes - types

        if newTypes:
            # Propagate any new registrations to this layers's parents.
            for parent in self.parents:
                parent.RegisterSubLayer(self)

        subLayer.AddParent(self)

    def HandleMessage(self, message):
        '''
            Process the message within this layer if it has a handler.
        '''
        handler = self.handlers.get(message.getType())
        if handler:
            handler(message)

    def DispatchToLowerLayers(self, ts, message):
        '''
            Dispatch a message to any lower layers that have registered for it.
        '''
        layers = self.registrations.get(message.getType(), [])
        for layer in layers:
            layer.Dispatch(ts, message)

    def Process(self, ts):
        '''
            Process the message queue.
            Either hand it off to the appropriate handler or pass it on to the appropriate upper/lower layer.
        '''
        # Grab a reference for the scheduler's queue, but don't pop it until the end.
        # While processing messages, some new messages may be generated and need queueing.
        qTs, q = self.scheduler.Peek()

        if ts != qTs:
            return None

        # While there are messages to handle, run the current layer handling and then pass it down to any lower layers.
        while q:
            m = q.pop()
            self.HandleMessage(m)
            self.DispatchToLowerLayers(ts, m)

        # The queue for this ts is now empty. Pop it to remove it from the scheduler.
        self.scheduler.Pop()

    def Dispatch(self, ts, message):
        '''
            Add a new message into the queue and process the entire queue.
        '''
        Log.debug(f'{self} dispatching {message} @ {ts}')
        self.AddMessage(ts, message)
        self.Process(ts)

    def __str__(self):
        return f'{self.id}'
