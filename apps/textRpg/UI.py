# UI utils to format the I/O

from ...src import Layer, Message

class UI(Layer.Layer):
    def __init__(self):
        super().__init__()
        self.handlers['PROMPT'] = self.HandlePrompt

    def getPromptStr(self, dPrompt):
        '''
            Generate a string representing the input prompt.
                The prompt should be a dict with at least the following hierarchy:
                    'text': <prompt>
                    'info': {
                        'options': [
                            {
                                'input': <inputName>,
                                'text': <promptText>,
                            },
                            ...
                        ]
                    }
        '''
        #print(f'Generating prompt from {dPrompt}')
        s = '\n'
        dInfo = dPrompt.get('info', {})
        s += dInfo.get('text', '<>')
        for dOption in dInfo.get('options', []):
            s += f'\n\t{dOption.get("input", "<>")}: {dOption.get("text", "")}'
        s += '\n'
        return s

    def HandlePrompt(self, message):
        dPrompt = message.GetData()

        s = self.getPromptStr(dPrompt)
        print(s)

        response = input(':')

        response = Message.Message(
            'INPUT',
            dest=message.GetSrc(),
            data=response,
            src=self.GetId(),
        )

        self.ScheduleMessageFor(0, response)