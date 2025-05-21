from uuid import uuid4

from interfaces import (
    IService,
    IFetcher,
    ILogger,
    DebugService,
    ReleaseService,
    SqlFetcher,
    MemoryFetcher,
    FileLogger,
    ConsoleLogger,
)
from injector import LifeStyle, Injector

def build_debug() -> Injector:
    injector = Injector()
    injector.register(ILogger, ConsoleLogger, LifeStyle.SINGLETON)
    injector.register(IFetcher, MemoryFetcher, LifeStyle.SCOPED)
    injector.register(
        IService,
        provider=lambda: DebugService(
            # Этот метод возвращает экземпляр объекта, реализующего указанный интерфейс.
            logger=injector.get_instance(ILogger),
            fetcher=injector.get_instance(IFetcher),
        ),
        lifestyle=LifeStyle.PER_REQUEST,
    )
    injector.register(str, lambda: str(uuid4()), LifeStyle.PER_REQUEST)
    return injector

def build_release() -> Injector:
    injector = Injector()
    injector.register(ILogger, FileLogger, LifeStyle.SINGLETON, params={"path": "app.log"})
    injector.register(IFetcher, SqlFetcher, LifeStyle.SCOPED)
    injector.register(
        IService,
        provider=lambda: ReleaseService(
            logger=injector.get_instance(ILogger),
            fetcher=injector.get_instance(IFetcher),
        ),
        lifestyle=LifeStyle.PER_REQUEST,
    )
    # устанавливает жизненный цикл и, опционально, предоставляет параметры для конструктора реализации
    injector.register(str, lambda: str(uuid4()), LifeStyle.PER_REQUEST)
    return injector


def demo(injector: Injector, tag: str):
    print(f"\n=== {tag} ===")
    # Создается только один экземпляр объекта на все приложение.
    print("Singleton logger:", injector.get_instance(ILogger), injector.get_instance(ILogger))
    # Scope 1
    # Создается один экземпляр объекта на область видимости (scope).
    # Область видимости определяется с помощью injector.create_scope().
    # Внутри области видимости всегда будет использоваться один и тот же экземпляр.
    with injector.create_scope():
        service_1 = injector.get_instance(IService)
        service_2 = injector.get_instance(IService)
        print("PerRequest service:", service_1, service_2)
        service_1.run()
        fetcher_1 = injector.get_instance(IFetcher)
        fetcher_2 = injector.get_instance(IFetcher)
        print("Scoped fetcher:", fetcher_1, fetcher_2)
    # Scope 2
    with injector.create_scope():
        print("New scope, new fetcher:", fetcher_1, injector.get_instance(IFetcher))
        injector.get_instance(IService).run()
    # PerRequests - Создается новый экземпляр объекта каждый раз, когда он запрашивается.
    print("uuid:", injector.get_instance(str))

if __name__ == "__main__":
    demo(build_debug(), "DEBUG")
    demo(build_release(), "RELEASE")
