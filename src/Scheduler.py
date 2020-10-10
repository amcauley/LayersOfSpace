'''
    Each Item will maintain its own scheduling list.
    For each timestamp where events need to be handled, there will be a queue of events to be handled at that time.
    Timestamp: X   X+1 X+2 ...
               Q   Q   Q

    The queue's are envisioned as having the next upcoming event on the right end, i.e. calling pop() will pop the
        next event to process, and calling popleft() would pop the event furthest in the future.
'''

from collections import deque

from . import SchedulingList

class Scheduler:
    def __init__(self):
        self.schedule = SchedulingList.SchedulingList()

    def Add(self, ts, event):
        '''
            Add an event at time ts into the tracked events queue for that time.
        '''
        e = self.schedule.Get(ts)
        if e is None:
            e = deque()
            self.schedule.Add(ts, e)

        e.appendleft(event)

    def Peek(self):
        '''
            Return the next (ts, event) tuple, or None if there are no scheduled events.
        '''
        return self.schedule.Peek()

    def Pop(self):
        '''
            The events are returned as a tuple: (timestamp, event).
                If no events are present, return None.
        '''
        return self.schedule.Pop()

    def Get(self, ts):
        '''
            Return the event queue for time ts if it exists, else None.
        '''
        return self.schedule.Get(ts)
