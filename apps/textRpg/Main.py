'''
    Simple "game" demo where the UI/client communicates in a loop with a game-logic "server".
'''
from . import Server
from . import UI

from ...src import Layer, Message

if __name__ == "__main__":
    # To run: "python -m LayersOfSpace.apps.textRpg.Main".

    top = Layer.Layer()
    top.SetId('Top')

    server = Server.Server()
    server.initSitutation('LayersOfSpace/apps/textRpg/Configs/Test.txt:First')
    server.SetId('Top.Server')

    ui = UI.UI()
    ui.SetId('Top.UI')

    top.RegisterSubLayer(server) 
    top.RegisterSubLayer(ui)

    promptMessage = Message.Message(
        'PROMPT',
        dest=ui.GetId(),
        data=server.getState(),
        src=server.GetId(),
    )

    top.ScheduleMessage(0, promptMessage)

    while(True):
        top.Process(0)
        break
