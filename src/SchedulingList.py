'''
    Underlying data structure for scheduling events.
    It should maintain a list/queue/etc. of events in the order in which they'll be run.
'''

import heapq

class SchedulingList:
    def __init__(self):
        # This is the underlying structure for the priority queue.
        self.events = []

        # Maintain a dict that maps event timestamps to those events.
        # This will be useful for quickly querying if there's an event at a certain time,
        # as well as for directly modifying the event (if it's an object).
        self.map = {}

    def Add(self, ts, event):
        '''
            Add an event at time ts into the tracked events.
        '''
        heapq.heappush(self.events, (ts, event))
        self.map[ts] = event

    def Get(self, ts):
        '''
            Returns an event if it exists at the specified timestamp, else None.
        '''
        return self.map.get(ts)

    def Pop(self):
        '''
            Pops the next event (return it and stop tracking it).
                The events are returned as a tuple: (timestamp, event).
                If no events are present, return None.
        '''
        if not self.map:
            return None
        else:
            t = heapq.heappop(self.events)
            ts, _event = t
            del self.map[ts]
            return t
