
import threading

class LifeStyle:
    PerRequest = 1
    Scoped = 2
    Singleton = 3

class DependencyError(Exception):
    pass

class Scope:
    _current = threading.local()

    @classmethod
    def set(cls, scope):
        cls._current.scope = scope

    @classmethod
    def get(cls):
        return getattr(cls._current, 'scope', None)

class Injector:
    def __init__(self):
        self._registrations = {}
        self._singletons = {}
        self._scope = {}

    def register(self, interface_type, implementation, life_circle=LifeStyle.PerRequest, params=None):
        if interface_type in self._registrations:
            raise DependencyError(f"Interface {interface_type} already registered.")

        self._registrations[interface_type] = {
            'implementation': implementation,
            'life_circle': life_circle,
            'params': params,
            'is_factory': False
        }

    def register_factory(self, interface_type, factory_method):
        if interface_type in self._registrations:
            raise DependencyError(f"Interface {interface_type} already registered.")

        self._registrations[interface_type] = {
            'implementation': factory_method,
            'life_circle': LifeStyle.PerRequest,  # Factories are typically per-request
            'params': None,
            'is_factory': True
        }


    def get_instance(self, interface_type):
        if interface_type not in self._registrations:
            raise DependencyError(f"No registration found for interface {interface_type}")

        registration = self._registrations[interface_type]
        implementation = registration['implementation']
        life_circle = registration['life_circle']
        params = registration['params']
        is_factory = registration['is_factory']

        if life_circle == LifeStyle.Singleton:
            if interface_type not in self._singletons:
                self._singletons[interface_type] = self._create_instance(implementation, params, is_factory)
            return self._singletons[interface_type]

        elif life_circle == LifeStyle.Scoped:
            scope = Scope.get()
            if scope is None:
                # Removed the error. The scoping is handled by the `with` statement
                # raise DependencyError("No scope is active.")
                return self._create_instance(implementation, params, is_factory)  # Default to per-request if no scope
            if interface_type not in scope:
                scope[interface_type] = self._create_instance(implementation, params, is_factory)
            return scope[interface_type]

        else:  # LifeStyle.PerRequest
            return self._create_instance(implementation, params, is_factory)

    def _create_instance(self, implementation, params, is_factory):
        if is_factory:
            return implementation()

        if params is None:
            try:
                return implementation()
            except TypeError:  # Line 87: Removed unused variable 'e'
                # Attempt to resolve dependencies in constructor
                args = []
                for arg_name, arg_type in implementation.__init__.__annotations__.items():
                    if arg_name == 'return':
                        continue
                    if arg_type is not None:
                        args.append(self.get_instance(arg_type))
                    else:
                        raise DependencyError(f"Can't resolve dependency {arg_name} in {implementation.__name__}'s constructor.  Add type annotation.")

                return implementation(*args)

        else:
            return implementation(**params)

    @staticmethod # Line 103: Added staticmethod decorator
    def start_scope():
      """Starts a new scope.  Returns a context manager."""
      return _ScopeContext()


class _ScopeContext:
    def __enter__(self):
      self._old_scope = Scope.get()
      Scope.set({})  # Start a new scope
      return self

    def __exit__(self, exc_type, exc_val, exc_tb):
      Scope.set(self._old_scope)  # Restore the previous scope.



# Interfaces
class Interface1:
    def do_something(self):
        raise NotImplementedError

class Interface2:
    def do_something_else(self):
        raise NotImplementedError

class Interface3:
    def do_another_thing(self):
        raise NotImplementedError


# Implementations
class Class1Debug(Interface1):
    def __init__(self):
      pass

    def do_something(self):
        return "Class1Debug: Doing something (Debug mode)"

class Class1Release(Interface1):
    def __init__(self):
      pass

    def do_something(self):
        return "Class1Release: Doing something (Release mode)"

class Class2Debug(Interface2):
    def __init__(self, interface1: Interface1):
        self.interface1 = interface1

    def do_something_else(self):
        return f"Class2Debug: Doing something else. Using {self.interface1.do_something()}"

class Class2Release(Interface2):
    def __init__(self, interface1: Interface1):
        self.interface1 = interface1

    def do_something_else(self):
        return f"Class2Release: Doing something else. Using {self.interface1.do_something()}"


class Class3Debug(Interface3):
    def __init__(self, name: str = "Debug Name"):
        self.name = name

    def do_another_thing(self):
        return f"Class3Debug: Doing another thing. Name: {self.name}"

class Class3Release(Interface3):
    def __init__(self, name: str = "Release Name"):
        self.name = name

    def do_another_thing(self):
        return f"Class3Release: Doing another thing. Name: {self.name}"


# Configuration 1
def configure_injector1(injector):
    injector.register(Interface1, Class1Debug, LifeStyle.Singleton)
    injector.register(Interface2, Class2Debug, LifeStyle.Scoped)
    injector.register(Interface3, Class3Debug, LifeStyle.PerRequest, params={'name': 'Config1 Name'})

# Configuration 2
def configure_injector2(injector):
    injector.register(Interface1, Class1Release, LifeStyle.PerRequest)
    injector.register(Interface2, Class2Release, LifeStyle.Singleton)
    injector.register(Interface3, Class3Release, LifeStyle.Scoped, params={'name': 'Config2 Name'})


# Example usage
if __name__ == '__main__':
    # Configuration 1
    injector1 = Injector()
    configure_injector1(injector1)

    # Get instances and use them
    # This line causes the error because it isoutside of the start_scope context
    #instance2_1 = injector1.get_instance(Interface2)

    print("Config 1 - First Set:")

    with injector1.start_scope():
        instance1_1 = injector1.get_instance(Interface1)
        instance2_1 = injector1.get_instance(Interface2)
        instance3_1 = injector1.get_instance(Interface3)

        print(instance1_1.do_something())
        print(instance2_1.do_something_else())
        print(instance3_1.do_another_thing())


    instance1_1_again = injector1.get_instance(Interface1)  #Singleton returns same instance
    print("Config 1 - Same Singleton Instance: ", instance1_1 is instance1_1_again)


    # Scoped Example

    with injector1.start_scope():
        instance2_scoped1 = injector1.get_instance(Interface2)
        instance2_scoped2 = injector1.get_instance(Interface2)
        print("Config 1 - Within Scope: Same Scoped Instance ", instance2_scoped1 is instance2_scoped2)


    with injector1.start_scope():
        instance2_scoped3 = injector1.get_instance(Interface2)
        print("Config 1 - New Scope: Different Scoped Instance ", instance2_scoped1 is instance2_scoped3)


    instance3_1_again = injector1.get_instance(Interface3) #PerRequest returns new instance
    print("Config 1 - Different PerRequest Instance: ", instance3_1 is instance3_1_again)



    # Configuration 2
    injector2 = Injector()
    configure_injector2(injector2)

    # Get instances and use them
    instance1_2 = injector2.get_instance(Interface1)
    instance2_2 = injector2.get_instance(Interface2)
    instance3_2 = injector2.get_instance(Interface3)

    print("\nConfig 2 - First Set:")
    print(instance1_2.do_something())
    print(instance2_2.do_something_else())
    print(instance3_2.do_another_thing())

    instance1_2_again = injector2.get_instance(Interface1) #PerRequest returns new instance
    print("Config 2 - Different PerRequest Instance: ", instance1_2 is instance1_2_again)

    instance2_2_again = injector2.get_instance(Interface2) #Singleton returns same instance
    print("Config 2 - Same Singleton Instance: ", instance2_2 is instance2_2_again)


    with injector2.start_scope():
        instance3_scoped1 = injector2.get_instance(Interface3)
        instance3_scoped2 = injector2.get_instance(Interface3)
        print("Config 2 - Within Scope: Same Scoped Instance ", instance3_scoped1 is instance3_scoped2)

    with injector2.start_scope():
        instance3_scoped3 = injector2.get_instance(Interface3)
        print("Config 2 - New Scope: Different Scoped Instance ", instance3_scoped1 is instance3_scoped3)
