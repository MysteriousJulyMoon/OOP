from core.injector import Injector
from core.lifecycle import LifeStyle
from services.service1.debug import DebugService1
from services.service2.debug import DebugService2
from services.service3.debug import DebugService3

def configure_debug_services(injector: Injector):
    injector.register(IInterface1, DebugService1, LifeStyle.SINGLETON)
    injector.register(IInterface2, DebugService2, LifeStyle.PER_REQUEST)
    injector.register(IInterface3, DebugService3, LifeStyle.SCOPED)