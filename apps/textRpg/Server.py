from . import Parser

from ...src import Layer, Message

class Server(Layer.Layer):
    def __init__(self):
        super().__init__()
        self.handlers['INPUT'] = self.HandleInput

        self.controller = Parser.Controller()
        self.dState = Parser.getDefaultUserDict()

    def initSitutation(self, situationStr):
        self.controller.getPrompt(situationStr, self.dState)

    def getState(self):
        return self.dState

    def HandleInput(self, message):
        i = message.GetData()
        print(f'Got input "{i}"')

        self.controller.getResponse(i, self.dState)

        promptMessage = Message.Message(
            'PROMPT',
            dest=message.GetSrc(),
            data=self.dState,
            src=self.GetId(),
        )

        self.ScheduleMessageFor(0, promptMessage)