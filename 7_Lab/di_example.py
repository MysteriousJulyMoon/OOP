from abc import ABC, abstractmethod
from dependency_injector import providers, containers

# Interfaces (Abstract Base Classes)
class IInterface1(ABC):
    @abstractmethod
    def operation1(self) -> str:
        pass


class IInterface2(ABC):
    @abstractmethod
    def operation2(self) -> str:
        pass


class IInterface3(ABC):
    @abstractmethod
    def operation3(self) -> str:
        pass


# Implementations
class Class1Debug(IInterface1):
    def operation1(self) -> str:
        return "Debug Operation 1"


class Class1Release(IInterface1):
    def __init__(self, prefix: str = ""):
        self._prefix = prefix

    def operation1(self) -> str:
        return f"{self._prefix}Release Operation 1"


class Class2Debug(IInterface2):
    def __init__(self, service1: IInterface1):
        self._service1 = service1

    def operation2(self) -> str:
        return f"Debug Operation 2 with {self._service1.operation1()}"


class Class2Release(IInterface2):
    def __init__(self, service1: IInterface1, suffix: str = ""):
        self._service1 = service1
        self._suffix = suffix

    def operation2(self) -> str:
        return f"Release Operation 2 with {self._service1.operation1()} {self._suffix}"


class Class3Debug(IInterface3):
    def __init__(self, service2: IInterface2):
        self._service2 = service2

    def operation3(self) -> str:
        return f"Debug Operation 3 with {self._service2.operation2()}"


class Class3Release(IInterface3):
    def __init__(self, service2: IInterface2, count: int = 1):
        self._service2 = service2
        self._count = count

    def operation3(self) -> str:
        return f"Release Operation 3 (x{self._count}) with {self._service2.operation2()}"


# Custom Factory Method (using provider)
class SpecialInterface2(providers.Factory):
    def __init__(self, service1: providers.Provider, suffix: str):
        super().__init__(Class2Release, service1=service1, suffix=suffix)


# Dependency Injection Container
class Container(containers.DeclarativeContainer):
    service1 = providers.AbstractProvider()  #Now AbstractProvider is used correctly
    service2 = providers.AbstractProvider()
    service3 = providers.AbstractProvider()


class DebugContainer(Container):
    service1 = providers.Singleton(Class1Debug)
    service2 = providers.Factory(Class2Debug, service1=service1)
    service3 = providers.Scoped(Class3Debug, service2=service2)


class ReleaseContainer(Container):
    prefix = providers.Configuration()
    count = providers.Configuration()

    service1 = providers.Singleton(Class1Release, prefix=prefix)
    service2 = SpecialInterface2(service1=service1, suffix="(special)")
    service3 = providers.Singleton(Class3Release, service2=service2, count=count)

    # Demonstration


def demonstrate_container(container: Container):
    print("Demonstrating container:")

    # Singleton demonstration
    instance1 = container.service1()
    instance2 = container.service1()
    print(f"Singleton instances equal: {instance1 is instance2}")
    print(f"Instance1 operation: {instance1.operation1()}")

    # Scoped demonstration - now correctly initialized
    with container.service3.context():
        scoped_instance1 = container.service3()
        scoped_instance2 = container.service3()
        print(f"Scoped instances equal: {scoped_instance1 is scoped_instance2}")
        print(f"Scoped instance operation: {scoped_instance1.operation3()}")
    # Factory demonstration
    instance = container.service2()
    print(f"Factory-created instance: {instance.operation2()}")


if __name__ == "__main__":
    # Debug configuration
    debug_container = DebugContainer()
    debug_container.service3.override(
        providers.Singleton(Class3Debug, service2=debug_container.service2))  # explicit service2
    print("=== Debug Configuration ===")
    demonstrate_container(debug_container)

    # Release configuration
    release_container = ReleaseContainer()
    release_container.prefix.from_value("PROD-")
    release_container.count.from_value(3)
    release_container.service3.override(providers.Singleton(Class3Release, service2=release_container.service2,
                                                            count=release_container.count()))  # explicit service2 and count
    print("\n=== Release Configuration ===")
    demonstrate_container(release_container)
