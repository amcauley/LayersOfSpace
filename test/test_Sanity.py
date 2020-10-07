# From the main directory, call 'python -m pytest test\test_Sanity.py to run this single file,
# or run 'python -m pytest test' to run all tests.

from collections import deque

from src import Scheduler, SchedulingList
from src.Log import Log

class TestClass():

    @classmethod
    def setup_class(cls):
        cls.schedulingList = SchedulingList.SchedulingList()
        cls.scheduler = Scheduler.Scheduler()

    def test_SchedulingList_Add_Get_Pop(self):
        entries = [
            (0, 'a'),
            (2, 'c'),
            (1, 'b'),
        ]

        sl = TestClass.schedulingList

        for entry in entries:
            sl.Add(*entry)

        entriesSorted = sorted(entries)
        for entrySorted in entriesSorted:
            Log.debug(entrySorted)
            ts, event = entrySorted
            assert(sl.Get(ts) == event)
            assert(sl.Pop() == entrySorted)

        assert(sl.Get(0) == None)
        assert(sl.Pop() == None)

    def test_Scheduler_Add_Pop(self):
        entries = [
            (0, 'a'),
            (2, 'c'),
            (1, 'b'),
        ]

        s = TestClass.scheduler

        for entry in entries:
            s.Add(*entry)

        # Note that the scheduler wraps entries in queues.
        entriesSorted = sorted(entries)
        for entrySorted in entriesSorted:
            Log.debug(entrySorted)
            ts, q = s.Pop()
            assert(ts == entrySorted[0])
            assert(q.pop() == entrySorted[1])

        assert(s.Pop() == None)

        # Check that entries to the same timestamp are placed in the same queue.
        sameTsEntries = ['x', 'y']
        for sameTsEntry in sameTsEntries:
            s.Add(0, sameTsEntry)

        q = s.Pop()[1]
        for sameTsEntry in sameTsEntries:
            assert(q.pop() == sameTsEntry)
