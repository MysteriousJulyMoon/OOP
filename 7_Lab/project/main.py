from core.injector import Injector
from config.debug import configure_debug_services
from config.release import configure_release_services
from interfaces.service1 import IInterface1
from interfaces.service2 import IInterface2
from interfaces.service3 import IInterface3


def demonstrate_injector(injector: Injector):


# Демонстрационная логика

if name == "__main__":
    # Debug конфигурация
    debug_injector = Injector()
    configure_debug_services(debug_injector)
    demonstrate_injector(debug_injector)

    # Release конфигурация
    release_injector = Injector()
    configure_release_services(release_injector)
    demonstrate_injector(release_injector)