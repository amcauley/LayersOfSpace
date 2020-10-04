'''
    The Layer class is an abstraction of basically any object ("Item", to avoid confusion with OOO coding terminology).
    It can be owned by parent Layers and own a collection of sub-Layers.
    At its heart, its job is to handle incoming messages by either processing them or routing them to another layer.
'''

from . import Message
from . import Scheduler

class Layer:
    def __init__(self):
        pass

    def Add(self, message, ts):
        '''
            Add a message into the queue at the provided timestamp (ts).
        '''
        pass

    def Process(self):
        pass

    def Dispatch(self):
        pass
