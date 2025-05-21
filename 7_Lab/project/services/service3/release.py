from interfaces.service2 import IInterface2
from interfaces.service3 import IInterface3


class ReleaseService3(IInterface3):
    def __init__(self, service2: IInterface2, count: int = 1):
        self._service2 = service2
        self._count = count

    def operation3(self) -> str:
        return f"Release Operation 3 (x{self._count}) with {self._service2.operation2()}"