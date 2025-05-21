from interfaces.service1 import IInterface1

class DebugService1(IInterface1):
    def operation1(self) -> str:
        return "Debug Operation 1"