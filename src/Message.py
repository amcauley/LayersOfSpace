'''
    Messages communicate events between different objects.

    At a minimum, they should contain:
        1. Type (str): Identifier for what kind of message this is.
        2. Data (no fixed type): Contents of the message.

    Sender and recipient information can be included in the data if needed.
    In many cases, the data field will just be a dictionary.
'''

class Message:
    def __init__(self, type, data=None):
        self.type = type
        self.data = data

    def getType(self):
        return self.type

    def setType(self, type):
        self.type = type

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data
