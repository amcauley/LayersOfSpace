import os

'''
    Groups of configs/prompts/etc. are separated by blank lines.
    Supported options:
        SIT <Situation_Name>
        SET <...> If no options are listed yet, unconditionally set these when entering the situation.
        CND <Condition> An optional condition needed to display following TXT.
        TXT <...> you can have all text on a single line using TXT.
        TXT<N> You can have text that spans N lines. Ex) TXT3 spans the 3 following lines.
            Useful for spaces, special formatting
        CND <Condition> An optional condition that's necessary to display next OPT.
        CND<N> Multiline conditions - one condition per supsequent line.
        OPT <Dest. Situation, Relative Path> <Option Text/Description>
        OPTN <...> Same as OPT, but with multiline support like TXT<N>.
'''

def onSIT(ln, dVars, dPrompt, dUser):
    '''
        SIT parser.
            Expected format: "SIT <Situation_Name>"

        :param ln: Input line to be parsed.
        :param dVars: Input state for the game vars.
        :param dPrompt: Input state for the current prompt group.
            See format notes within the Controller class.

        :returns: None, although dVars and/or dPrompt can be modified.
    '''
    name = ln.split()[1]
    dPrompt['info']['name'] = name

def onTXT(ln, dVars, dPrompt, dUser):
    '''
        TXT parser. See onSIT() for more param/return details.
            Expected format: "TXT blah blah blah ..."
    '''
    text = ln[len('TXT '):]
    dPrompt['info']['text'] = text

def onOPT(ln, dVars, dPrompt, dUser):
    '''
        OPT parser. See onSIT() for more param/return details.
            Expected format: "OPT <Dest. Situation, Relative Path> <Option Text/Description>"
    '''
    split = ln.split()

    pathRel = split[1]
    if (-1 == pathRel.find(':')):
        basePath = dPrompt['state']['path']
        lastColonIdx = basePath.rfind(':')
        path = basePath[:lastColonIdx + 1] + pathRel
    else:
        path = os.path.join(os.path.dirname(dPrompt['state']['path']), pathRel)
    pathAbs = os.path.abspath(path)

    offset = len('OPT ') + len(pathRel) + 1
    textRaw = ln[offset:]
    text = textRaw.rstrip('\r\n')

    dPrompt['info']['options'].append({
        'input': str(len(dPrompt['info']['options']) + 1),
        'text': text,
        'dest': pathAbs,
    })

CMD_HANDLERS = {
    'SIT': onSIT,
    'TXT': onTXT,
    'OPT': onOPT,
}

def getDefaultUserDict():
    return {
        'info': {}
    }

class Controller:
    def __init__(self):
        self.reset()

    def reset(self):
        ''' Clear state. '''
        # Structure storing prompt parsing info.
        # {
        #   'info': {
        #       'name': Situation/Prompt name
        #       'text': Prompt text
        #       'options': [
        #           {
        #               'input': Input key, string, etc.
        #               'text': Text associated with the option
        #               'dest': Destination prompt path (full)
        #           },
        #           ...
        #       ],
        #   },
        #
        #   'state': {
        #       'path': Current prompt path (full)
        #       'cond': {
        #           'bActive': Whether a condition is considered active/applicable
        #           'bVal': True/False state of the active condition
        #       },
        #   }
        # }
        self.resetPrompt()

        # Game vars/state.
        self.dVars = {}

    def resetPrompt(self):
        self.dPrompt = {
            'info': {'options': []},
            'state': {},
        }

    def getPrompt(self, option, dUser):
        '''
            Generate the specified prompt by parsing the source config and applying any necessary filtering.
                Input state, i.e. a dict vars used in the filtering.

            :param option: Path to the option to parse.
                The format is expected to be full/path/to/source/filename.ext:Situation_Name

            :param dUser: Dict of user-specific data/state.
                Includes the following fields (and possibly others):
                    {
                        'info': active info for this user, see format description in reset().
                    }

            :return: None, dUser is modified in place.
        '''
        self.resetPrompt()
        self.dPrompt['state']['path'] = option
        print(f'getPrompt for "{option}"')

        split = option.split(':')
        filePath = ':'.join(split[:-1])
        sitName = split[-1]

        with open(filePath, 'r') as f:
            lines = f.readlines()
            bTargetBlock = False

            for line in lines:
                lineSplit = line.split()
                cmdType = '' if not lineSplit else lineSplit[0]
                bTargetBlock = bTargetBlock or (('SIT' == cmdType) and (sitName == lineSplit[1]))

                if not bTargetBlock:
                    continue

                handler = CMD_HANDLERS.get(cmdType)
                if handler is None:
                    print(f'No handler found for cmd "{cmdType}"')
                    bTargetBlock = False
                    continue

                handler(line, self.dVars, self.dPrompt, dUser)

        dUser['info'] = self.dPrompt['info']

    def getResponse(self, input, dUser):
        '''
            Get the next prompt by applying input to the current game state.

            :param input: Input option, i.e. user's selection for the current prompt.
        '''
        for option in dUser['info']['options']:
            if input == option['input']:
                self.getPrompt(option['dest'], dUser)
                break
        else:
            print(f'Unexpected input "{input}"')

if __name__ == '__main__':
    # Quick demo based on Test.txt. Not yet interactive - input(s) are hardcoded.
    controller = Controller()
    dUser = getDefaultUserDict()

    controller.getPrompt('Test.txt:First', dUser)
    print(dUser)

    controller.getResponse('1', dUser)
    print(dUser)
