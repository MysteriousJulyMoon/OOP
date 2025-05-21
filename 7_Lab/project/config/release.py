from core.injector import Injector
from core.lifecycle import LifeStyle
from interfaces.service1 import IInterface1
from interfaces.service2 import IInterface2
from interfaces.service3 import IInterface3
from services.service1.release import ReleaseService1
from services.service2.release import create_special_service2
from services.service3.release import ReleaseService3

def configure_release_services(injector: Injector):
    injector.register(
        IInterface1,
        ReleaseService1,
        LifeStyle.SINGLETON,
        {'prefix': 'PROD-'}
    )
    injector.register(
        IInterface2,
        create_special_service2,
        LifeStyle.SCOPED
    )
    injector.register(
        IInterface3,
        ReleaseService3,
        LifeStyle.SINGLETON,
        {'count': 3}
    )