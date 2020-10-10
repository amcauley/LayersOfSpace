# From the main directory, call 'python -m pytest -v test\test_Layer.py to run this single file,
# or run 'python -m pytest test' to run all tests.

from src import Layer, Message
from src.Log import Log

class _TestLayerWithHandler(Layer.Layer):
    # Used for tracking the order in which test layer handlers are called.
    calls = []

    def __init__(self):
        super().__init__()
        self.handlers['TEST_MESSAGE_TYPE'] = self.TestMessageHandler

    def TestMessageHandler(self, message):
        if not self.parents:
            Log.debug(f'{self} clearing calls')
            _TestLayerWithHandler.calls = []
        _TestLayerWithHandler.calls.append(str(self))
        Log.debug(f'{self.id} handling {message}')

class _TestLayerWithHandlerAndId(_TestLayerWithHandler):
    def __init__(self):
        super().__init__()

        del self.handlers['TEST_MESSAGE_TYPE']
        self.handlers['TEST_MESSAGE_ALT_TYPE'] = self.TestMessageHandler

    def NewChildId(self):
        return f'{self.id}.TestID'

class TestClass():

    @classmethod
    def setup_class(cls):
        #       A(0)
        #      / \
        #     v   v
        # B(0.0)  C(0.1) -> X(0.1.2) -> Y(0.1.TestID)
        #         |  \
        #         v   v
        #  D(0.1.0) -> M(0.1.1)
        TestClass.layerA = _TestLayerWithHandler()
        TestClass.layerB = _TestLayerWithHandler()
        TestClass.layerC = _TestLayerWithHandler()
        TestClass.layerD = _TestLayerWithHandler()
        TestClass.layerM = _TestLayerWithHandler()

        TestClass.layerX = _TestLayerWithHandlerAndId()
        TestClass.layerY = _TestLayerWithHandlerAndId()

    def test_Parent_And_Child(self):
        TestClass.layerA.SetId('0')
        TestClass.layerA.RegisterSubLayer(TestClass.layerB)
        TestClass.layerA.RegisterSubLayer(TestClass.layerC)
        TestClass.layerC.RegisterSubLayer(TestClass.layerD)
        TestClass.layerC.RegisterSubLayer(TestClass.layerM)
        TestClass.layerD.RegisterSubLayer(TestClass.layerM)

        TestClass.layerC.RegisterSubLayer(TestClass.layerX)
        TestClass.layerX.RegisterSubLayer(TestClass.layerY)

        testMessage = Message.Message(
            'TEST_MESSAGE_TYPE',
            dest=TestClass.layerA.GetId(),
            data='TEST_DATA',
            prop=Message.PROP_ALL)

        TestClass.layerA.AddMessage(0, testMessage)
        TestClass.layerA.Process(0)

        # Both C and D will forward the message to M.
        assert(_TestLayerWithHandler.calls == ['0', '0.0', '0.1', '0.1.0', '0.1.1', '0.1.1'])

    def test_Notification_Scheduling(self):
        testMessage = Message.Message(
            'TEST_MESSAGE_ALT_TYPE',
            dest=TestClass.layerY.GetId(),
            data='TEST_DATA',
            prop=Message.PROP_EXACT)

        _TestLayerWithHandler.calls = []

        TestClass.layerY.ScheduleMessage(0, testMessage)
        TestClass.layerA.Process(0)

        # Notifications don't trigger handlers except at the destination.
        assert(_TestLayerWithHandler.calls == ['0.1.2.TestID'])