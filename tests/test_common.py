import pygame_dps_core.common as common


class SignalObject(common.Node):
    test: common.Signal

    def _on_enter(self):
        return super()._on_enter()

    def _on_exit(self):
        return super()._on_exit()

    def _update(self, dt: float):
        return super()._update(dt)


def test_signal_instances():
    a = SignalObject()
    b = SignalObject()

    assert a.test != b.test
    assert a.test.obj != b.test.obj
