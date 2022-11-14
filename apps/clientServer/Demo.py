'''
This demo shows an implementation of a separated client and target, i.e. the client UI and backend server/target are
separate entities. This is similar to the situation where the client and server could be on separate machines.

To Run: "python -m LayersOfSpace.apps.clientServer.Demo"

There are drawbacks to this design for a real prompt/response application, namely latency in synchronizing components.
For a more responsive text-based prompt/response example, see the textRpg folder.

The following diagram shows the processing loop used in the demo:

Client                                         Target

show prompt   <--------------------------------------
|                                                   |
V                                                   |
prompt response                                     |
|                                                   |
V                                                   |
qToUser                                             |
|                                                   |
V                                                   |
user input                                          |
|                                                   |
V                                                   |
MOVEMENT                                            |
|                                                   |
V                wakeup timer                       |
qFromUser ------------------------> HandleMovement  |
                                            |       |
                                            V       |
                                        next PROMPT_DATA
'''

from queue import Queue
from threading import Thread
import time

from ...src import Layer, Message
from ...src.Log import Log

PROMPT_DATA = {
    'bResponse': True,
    'text': 'Enter Movement:\n\tu: up,\n\td: down\n\tl: left\n\tr: right'
}

class Target(Layer.Layer):
    locX = 0
    locY = 0

    def __init__(self):
        super().__init__()
        self.handlers['MOVEMENT'] = self.HandleMovement

    def HandleMovement(self, message):
        Log.debug(f'Target {self} received movement {message}')

        deltaX, deltaY = message.GetData()
        Target.locX += deltaX
        Target.locY += deltaY

        Log.debug(f'Location: {(Target.locX, Target.locY)}')

        # ScheduleMessageFor client
        response = Message.Message(
            'PROMPT',
            dest=message.GetSrc(),
            data=PROMPT_DATA,
            src=self.GetId(),
        )

        self.ScheduleMessageFor(0, response)

# May need a separate thread within the UI thread to collect user inputs.
# Can't do this within the main uiThread since we don't want to block any messages while scanning for inputs.
# May also need a separate display thread to display those messages.

def uiThread(qToUser, qFromUser):
    while True:
        while not qToUser.empty():
            message = qToUser.get()
            Log.debug(f'UI Thread, ts {message.GetData()}')
            qToUser.task_done()

            d = message.GetData()
            if d.get('bResponse', False):
                print(d.get('text'))
                i = input('')

                if 'u' == i:
                    m = (0, 1)
                elif 'd' == i:
                    m = (0, -1)
                elif 'l' == i:
                    m = (-1, 0)
                elif 'r' == i:
                    m = (1, 0)

                movementMessage = Message.Message(
                    'MOVEMENT',
                    dest=message.GetSrc(),
                    data=m,
                )

                qFromUser.put(movementMessage)

class Client(Layer.Layer):
    def __init__(self):
        super().__init__()
        self.handlers['PROMPT'] = self.PromptResponse
        self.handlers['WAKEUP'] = self.HandleWakeup

        self.qToUser = Queue(maxsize=0)
        self.qFromUser = Queue(maxsize=0)

        ui = Thread(target=uiThread, args=(self.qToUser, self.qFromUser))
        ui.daemon = True
        ui.start()

    def HandleWakeup(self, message):
        # This is triggered by the main thread.
        # Check the qFromUser queue for any responses that need to be picked up and processed.
        Log.debug('Client received periodic wakeup')

        while not self.qFromUser.empty():
            message = self.qFromUser.get()
            message.SetSrc(self.GetId())
            self.ScheduleMessageFor(0, message)
            self.qFromUser.task_done()

    def PromptResponse(self, message):
        # Responses should be forwarded to the UI.
        Log.debug(f'Client {self} received prompt {message}')
        self.qToUser.put(message)

if __name__ == "__main__":
    top = Layer.Layer()
    top.SetId('Top')

    target = Target()
    target.SetId('Top.Target')

    client = Client()
    client.SetId('Top.Client')

    top.RegisterSubLayer(target)
    top.RegisterSubLayer(client)

    promptMessage = Message.Message(
        'PROMPT',
        dest=client.GetId(),
        data=PROMPT_DATA,
        src=target.GetId(),
    )

    target.ScheduleMessage(0, promptMessage)

    wakeupMessage = Message.Message(
        'WAKEUP',
        dest=top.GetId(),
        prop=Message.PROP_ALL,
    )

    ts = 0
    while True:
        wakeupMessage.SetData(ts)
        top.ScheduleMessage(ts, wakeupMessage)
        top.Process(ts)
    
        # TODO: Need to a way to schedule for a time, ex. schedule for timestamp x.
        # The issue is that by the time the message is processed, it might be a long time in the past.
        # Need to implement a timeout mechanism for schedulers and processors, i.e. what if the timestamp has passed already?
        # For now, just keep reusing the same timestamp.
        #ts += 1

        time.sleep(6.0)