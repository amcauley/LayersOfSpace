# From the main directory, call 'python -m pytest test\test_Layer.py to run this single file,
# or run 'python -m pytest test' to run all tests.

from src import Layer, Message
from src.Log import Log

TEST_MESSAGE = Message.Message('TEST_MESSAGE_TYPE', 'TEST_DATA')

class _TestLayer(Layer.Layer):
    # Used for tracking the order in which test layer handlers are called.
    calls = []

    def __init__(self, id):
        super().__init__(id)

        self.handlers = {
            'TEST_MESSAGE_TYPE': self.TestMessageHandler,
        }

    def TestMessageHandler(self, message):
        if not self.parents:
            Log.debug(f'{self} clearing calls')
            _TestLayer.calls = []
        _TestLayer.calls.append(str(self))
        Log.debug(f'{self.id} handling {message}')

class TestClass():

    @classmethod
    def setup_class(cls):
        #       A
        #      / \
        #     B   C
        #         | \
        #         D - M
        TestClass.layerA = _TestLayer('A')
        TestClass.layerB = _TestLayer('A.B')
        TestClass.layerC = _TestLayer('A.C')
        TestClass.layerD = _TestLayer('A.C.D')
        TestClass.layerM = _TestLayer('M')

    def test_Parent_And_Child(self):
        TestClass.layerA.RegisterSubLayer(TestClass.layerB)
        TestClass.layerA.RegisterSubLayer(TestClass.layerC)
        TestClass.layerC.RegisterSubLayer(TestClass.layerD)
        TestClass.layerC.RegisterSubLayer(TestClass.layerM)
        TestClass.layerD.RegisterSubLayer(TestClass.layerM)

        TestClass.layerA.Dispatch(0, TEST_MESSAGE)

        # Both C and D will forward the message to M.
        assert(_TestLayer.calls == ['A', 'A.B', 'A.C', 'A.C.D', 'M', 'M'])

        #assert(False)
