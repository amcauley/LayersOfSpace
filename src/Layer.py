'''
    The Layer class is an abstraction of basically any object ("Item", to avoid confusion with OOO coding terminology).
    It can be owned by parent Layers and own a collection of sub-Layers.
    At its heart, its job is to handle incoming messages by either processing them or routing them to another layer.
'''

from . import Message, Scheduler
from .Log import Log

class Layer:
    def __init__(self):
        # Id holds the unique identifier string for this instance.
        # By default it's None. It won't be assigned a value until this Item is registered to a parent.
        # The idea is that until it's registered, a name is meaningless, and the parent (owner) should
        # have rights to name its children in a way that makes sense for its purposes.
        self.id = None
        self.idCntr = 0

        # Tracks upcoming events that this layer needs to know about.
        self.scheduler = Scheduler.Scheduler()

        # Map message type -> handlers this layer will use for its own processing.
        self.handlers = {
            Message.TYPE_NOTIFICATION: [self.OnNotification]
        }

        # Map message type -> sub layers registered to process them.
        self.registrations = {}

        # Layers that list this one as a sub-layer.
        self.parents = []

    def GetId(self):
        return self.id

    def SetId(self, id):
        self.id = id

    def OnNotification(self):
        pass

    def AddMessage(self, ts, message):
        '''
            Simple message adding routine.
                Use ScheduleMessage if you want the proper upper/lower layers to schedule notifications.
        '''
        Log.debug(f'Layer {self} added {message.GetType()} w/dest {message.GetDest()}')
        self.scheduler.Add(ts, message)

    def ScheduleMessage(self, ts, message):
        '''
            Add a message into the scheduler at the provided timestamp (ts),
                then register notification triggers with parents if not already registered.

            It's expected that the destination is the current layer or a sublayer.

            If you want to schedule on behalf of another layer, including higher ones or ones in parallel braches,
                use ScheduleMessageFor(...).   
        '''
        type = message.GetType()

        # Notifications should be scheduled in the current layer directly
        dest = message.GetDest()

        if (type == Message.TYPE_NOTIFICATION) or (dest == self.id):
            e = self.scheduler.Get(ts)
            self.AddMessage(ts, message)

            # Create a notification to higher layers that can trigger processing in this layer at the appropriate time.
            # If events were already scheduled for the target ts, assume this has already been done previously.
            if not e:
                notification = Message.Notification(self.id)

                for parent in self.parents:
                    parent.ScheduleMessage(ts, notification)

        elif message.DestIsSubLayerOrEqualTo(self):
            # Pass the message down to sublayers on the path to its destination.
            for subLayer in self.GetSubLayers():
                if message.DestIsSubLayerOrEqualTo(subLayer):
                    subLayer.ScheduleMessage(ts, message)

        else:
            for parent in self.parents:
                parent.ScheduleMessage(ts, message)

    def ScheduleMessageFor(self, ts, message):
        '''
            Schedule a message on behalf of the destination layer.
                Return True if successful.
        '''
        # Navigate to the proper destination then run normal scheduling.
        dest = message.GetDest()

        Log.debug(f'Layer {self} scheduling {message.GetType()} for {dest}')

        if dest == self.id:
            self.ScheduleMessage(ts, message)
            return True

        elif message.DestIsSubLayerOrEqualTo(self):
            for subLayer in self.GetSubLayers():
                if message.DestIsSubLayerOrEqualTo(subLayer):
                    if subLayer.ScheduleMessageFor(ts, message):
                        return True
            return False

        else:
            for parent in self.parents:
                if parent.ScheduleMessageFor(ts, message):
                    return True
            return False

    def AddParent(self, parentLayer):
        if parentLayer not in self.parents:
            self.parents.append(parentLayer)

    def GetMessageTypes(self):
        '''
            Returns a set of message types handled by this sub-layer instance.
                This is per-instance and includes any types registered to this particular instance.
        '''
        return set(self.handlers.keys()).union(set(self.registrations.keys()))

    def NewChildId(self):
        '''
            This function returns a new child ID based on sequential numbering.
                It can be overridden if more complicated or descriptive naming schemes are desired.
        '''
        self.idCntr += 1
        return f'{self.id}.{self.idCntr-1}'

    def SetChildId(self, subLayer):
        '''
            Generate, apply, and return an ID for newly registering subLayer. 
                If it already has an ID that doesn't conflict with other subLayers, just keep using it.
                If an ID exists but conflicts, return None.
        '''
        childId = None
        existingId = subLayer.GetId()

        if existingId is None:
            childId = self.NewChildId()
            subLayer.SetId(childId)
        elif existingId not in self.registrations.values():
            childId = existingId

        return childId

    def GetSubLayers(self):
        # All layers are expected to register for notifications.
        return self.registrations.get(Message.TYPE_NOTIFICATION, [])

    def RegisterSubLayer(self, subLayer):
        '''
            (Re-)Register a sub-layer, i.e. identify which message types it can handle.
                Return the name if the registered SubLayer.
                Return None if registration failed.
        '''
        id = self.SetChildId(subLayer)
        if id is None:
            Log.warning('Failed to register subLayer; ID creation failed')
            return None

        types = self.GetMessageTypes()
        subTypes = subLayer.GetMessageTypes() 

        for type in subTypes:
            typeRegistrations = self.registrations.setdefault(type, [])
            if subLayer not in typeRegistrations:
                typeRegistrations.append(subLayer)
                Log.debug(f'Layer {self} registered message type {type} to subLayer {subLayer}')    

        newTypes = subTypes - types

        if newTypes:
            # Propagate any new registrations to this layers's parents.
            for parent in self.parents:
                parent.RegisterSubLayer(self)

        subLayer.AddParent(self)
        return id

    def HandleMessage(self, message):
        '''
            Process the message within this layer if it has a handler.
        '''
        handler = self.handlers.get(message.GetType())
        if handler:
            handler(message)

    def NotifyLowerLayers(self, ts, message):
        '''
            Process notifications to trigger lower layers if they're viable destinations.
        '''
        layers = self.GetSubLayers()
        for layer in layers:
            if message.DestIsSubLayerOrEqualTo(layer):
                layer.Process(ts)

    def Process(self, ts):
        '''
            Process the message queue.

            Either hand it off to the appropriate handler or pass it on to the appropriate upper/lower layer.
        '''
        # Grab a reference for the scheduler's queue, but don't pop it until the end.
        # While processing messages, some new messages may be generated and need queueing.
        qTs, q = self.scheduler.Peek()

        Log.debug(f'Processing Layer {self}: {len(q)} queued message(s)')

        if ts != qTs:
            return None

        # While there are messages to handle, run the current layer handling and then pass it down to any lower layers.
        while q:
            m = q.pop()

            type = m.GetType()
            if type == Message.TYPE_NOTIFICATION:
                self.NotifyLowerLayers(ts, m)

            elif m.dest == self.id:
                if m.PropTargetsEqual():
                    self.HandleMessage(m)

                if m.PropTargetsLower():
                    for subLayer in self.registrations.get(type, []):
                        subLayer.AddMessage(ts, m.LowerEqCopy(newDest=subLayer.GetId()))
                        subLayer.Process(ts)

                if m.PropTargetsHigher():
                    for parent in self.parents:
                        parent.AddMessage(ts, m.HigherEqCopy(newDest=parent.GetId()))
                        parent.Process(ts)

        # The queue for this ts is now empty. Pop it to remove it from the scheduler.
        self.scheduler.Pop()

    def __str__(self):
        return f'{self.id}'
