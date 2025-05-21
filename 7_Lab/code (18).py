
from abc import ABC, abstractmethod
from enum import Enum

class LifeStyle(Enum):
    Singleton = 1
    Scoped = 2
    PerRequest = 3

# Define Interfaces
class Interface1(ABC):
    @abstractmethod
    def do_something(self):
        pass

class Interface2(ABC):
    @abstractmethod
    def do_something_else(self):
        pass

class Interface3(ABC):
    @abstractmethod
    def do_another_thing(self):
        pass

# Implementations for Debug
class Class1Debug(Interface1):
    def do_something(self):
        return "Class1Debug: Doing something (Debug)"

class Class2Debug(Interface2):
    def __init__(self, interface1: Interface1):
        self.interface1 = interface1

    def do_something_else(self):
        return f"Class2Debug: Doing something else. Using {self.interface1.do_something()}"

class Class3Debug(Interface3):
    def __init__(self, name: str = "Debug Name"):
        self.name = name

    def do_another_thing(self):
        return f"Class3Debug: Doing another thing. Name: {self.name}"

# Implementations for Release
class Class1Release(Interface1):
    def do_something(self):
        return "Class1Release: Doing something (Release)"

class Class2Release(Interface2):
    def __init__(self, interface1: Interface1):
        self.interface1 = interface1

    def do_something_else(self):
        return f"Class2Release: Doing something else. Using {self.interface1.do_something()}"

class Class3Release(Interface3):
    def __init__(self, name: str = "Release Name"):
        self.name = name

    def do_another_thing(self):
        return f"Class3Release: Doing another thing. Name: {self.name}"

class Injector:
    def __init__(self):
        self.bindings = {}
        self.singleton_instances = {}
        self.scoped_instances = {}
        self.current_scope = None

    def register(self, interface, implementation, lifestyle, params=None):
        self.bindings[interface] = (implementation, lifestyle, params)

    def get_instance(self, interface):
        implementation, lifestyle, params = self.bindings[interface]

        if lifestyle == LifeStyle.Singleton:
            if interface not in self.singleton_instances:
                self.singleton_instances[interface] = self._create_instance(implementation, params)
            return self.singleton_instances[interface]
        elif lifestyle == LifeStyle.Scoped:
            if self.current_scope is None:
                raise Exception("Cannot create a scoped instance outside of a scope.")
            if interface not in self.scoped_instances.get(self.current_scope, {}):
                if self.current_scope not in self.scoped_instances:
                    self.scoped_instances[self.current_scope] = {}
                self.scoped_instances[self.current_scope][interface] = self._create_instance(implementation, params)
            return self.scoped_instances[self.current_scope][interface]
        elif lifestyle == LifeStyle.PerRequest:
            return self._create_instance(implementation, params)
        else:
            raise ValueError(f"Unknown lifestyle: {lifestyle}")


    def _create_instance(self, implementation, params=None):
        if params:
            return implementation(**params)
        else:
            # Resolve dependencies if any.  In this simple example, we assume constructor injection
            # and only handle the special case of Class2 needing Interface1
            if implementation in (Class2Debug, Class2Release):
                interface1 = self.get_instance(Interface1)  # Resolve Interface1 dependency
                return implementation(interface1)

            return implementation()

    def start_scope(self):
        scope_id = id(object()) # Generate unique scope id
        self.current_scope = scope_id
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.current_scope in self.scoped_instances:
            del self.scoped_instances[self.current_scope]
        self.current_scope = None


# Функции конфигурации для инжектора зависимостей
def configure_injector1(injector):
    injector.register(Interface1, Class1Debug, LifeStyle.Singleton)
    injector.register(Interface2, Class2Debug, LifeStyle.Scoped)
    injector.register(Interface3, Class3Debug, LifeStyle.PerRequest, params={'name': 'Config1 Name'})

def configure_injector2(injector):
    injector.register(Interface1, Class1Release, LifeStyle.PerRequest)
    injector.register(Interface2, Class2Release, LifeStyle.Singleton)
    injector.register(Interface3, Class3Release, LifeStyle.Scoped, params={'name': 'Config2 Name'})

if __name__ == '__main__':
    injector1 = Injector()
    configure_injector1(injector1)

    print("Config 1 - First Set:")
    with injector1.start_scope():
        instance1_1 = injector1.get_instance(Interface1)
        instance2_1 = injector1.get_instance(Interface2)
        instance3_1 = injector1.get_instance(Interface3)

        print(instance1_1.do_something())
        print(instance2_1.do_something_else())
        print(instance3_1.do_another_thing())

    instance1_1_again = injector1.get_instance(Interface1)
    print("Config 1 - Same Singleton Instance: ", instance1_1 is instance1_1_again)

    with injector1.start_scope():
        instance2_scoped1 = injector1.get_instance(Interface2)
        instance2_scoped2 = injector1.get_instance(Interface2)
        print("Config 1 - Within Scope: Same Scoped Instance ", instance2_scoped1 is instance2_scoped2)

    with injector1.start_scope():
        instance2_scoped3 = injector1.get_instance(Interface2)
        print("Config 1 - New Scope: Different Scoped Instance ", instance2_scoped1 is instance2_scoped3)

    instance3_1_again = injector1.get_instance(Interface3)
    print("Config 1 - Different PerRequest Instance: ", instance3_1 is instance3_1_again)

    if __name__ == '__main__':
        injector2 = Injector()
        configure_injector2(injector2)
        print("\nConfig 2 - First Set:")
        with injector2.start_scope():
            instance1_2 = injector2.get_instance(Interface1)
            instance2_2 = injector2.get_instance(Interface2)
            instance3_2 = injector2.get_instance(Interface3)

            print(instance1_2.do_something())
            print(instance2_2.do_something_else())
            print(instance3_2.do_another_thing())

        instance1_2_again = injector2.get_instance(Interface1)
        print("Config 2 - Different PerRequest Instance: ", instance1_2 is instance1_2_again)

        instance2_2_again = injector2.get_instance(Interface2)
        print("Config 2 - Same Singleton Instance: ", instance2_2 is instance2_2_again)
        with injector2.start_scope():
            instance3_scoped1 = injector2.get_instance(Interface3)
            instance3_scoped2 = injector2.get_instance(Interface3)
            print("Config 2 - Within Scope: Same Scoped Instance ", instance3_scoped1 is instance3_scoped2)
        with injector2.start_scope():
            instance3_scoped3 = injector2.get_instance(Interface3)
            print("Config 2 - New Scope: Different Scoped Instance ", instance3_scoped1 is instance3_scoped3)

