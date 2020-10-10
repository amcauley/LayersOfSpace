'''
    Messages communicate events between different objects.

    They contain:
        1. Type (str): Identifier for what kind of message this is.
        2. Dest (str): Id of the destination Item.
        3. Prop (str): Method of propagating to other layers starting from Dest.
            See the PROP_* types defined in this file.
        4. Src (str): Id of the originating Item.
        5. Data (no fixed type): Contents of the message.

    In many cases, the data field will just be a dictionary.
'''

TYPE_NOTIFICATION = '!'

PROP_EXACT  = '='   # Exact match, don't propagate to other layers.
PROP_LT     = '<'   # Propagate to lower values, skip the actual destination layer.
PROP_LTE    = '['   # Propagate to lower values, include the current layer.
PROP_GT     = '>'   # Greater than version of PROP_LT.
PROP_GTE    = ']'   # Greater than version of PROP_LTE.
PROP_BI     = 'B'   # Bidirectional propagation, skip the destination.
PROP_ALL    = '*'   # Propagate in both directions and include the destination.

class Message:
    def __init__(self, type, dest, src=None, data=None, prop=PROP_EXACT):
        self.type = type
        self.dest = dest
        self.prop = prop
        self.src = src
        self.data = data

    def GetType(self):
        return self.type

    def GetDest(self):
        return self.dest

    def GetSrc(self):
        return self.src

    def GetData(self):
        return self.data

    def DestIsSubLayerOrEqualTo(self, ref):
        return self.dest.startswith(ref.GetId())

    def PropTargetsLower(self):
        return self.prop in [PROP_ALL, PROP_BI, PROP_LT, PROP_LTE]

    def PropTargetsHigher(self):
        return self.prop in [PROP_ALL, PROP_BI, PROP_GT, PROP_GTE]

    def PropTargetsEqual(self):
        return self.prop in [PROP_EXACT, PROP_ALL, PROP_LTE, PROP_GTE]

    def LowerEqCopy(self, newDest=None):
        return Message(
            self.type,
            newDest or self.dest,
            src=self.src,
            data=self.data,
            prop=PROP_LTE,
        )

    def HigherEqCopy(self, newDest=None):
        return Message(
            self.type,
            newDest or self.dest,
            src=self.src,
            data=self.data,
            prop=PROP_GTE,
        )

    def __str__(self):
        return f'<{self.type}: d: {self.dest}, s: {self.src}: {self.data}>'

def Notification(tgtId):
    return Message(
        TYPE_NOTIFICATION,
        tgtId,
        src=tgtId
    )
