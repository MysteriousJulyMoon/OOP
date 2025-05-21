import typing as t
from enum import Enum, auto
from contextlib import contextmanager


T = t.TypeVar("T")

# Определяет возможные жизненные циклы для зарегистрированных зависимостей
class LifeStyle(Enum):
    PER_REQUEST = auto()  # Каждый раз при запросе создается новый экземпляр.
    SCOPED = auto()  # Один экземпляр на область видимости (scope). Области видимости управляются с помощью контекстного менеджера create_scope.
    SINGLETON = auto()  # Только один экземпляр создается на все время работы Injector.

# Хранит информацию о зарегистрированной зависимости:
class _Registration:
    def __init__(
        self,
        provider: t.Callable[..., t.Any] | type[t.Any],  # Класс или функция(фабрика),создает экземпляр зависимости.
        lifestyle: LifeStyle,
        params: dict[str, t.Any] | None, # Словарь с параметрами, которые нужно передать в конструктор класса
    ) -> None:
        self.provider = provider
        self.lifestyle = lifestyle
        self.params = params or {}

class Injector:  # класс, который управляет зависимостями:
    def __init__(self) -> None:
        self._registrations: dict[type[t.Any], _Registration] = {}
        self._singletons: dict[type[t.Any], t.Any] = {}
        self._scope_stack: list[dict[type[t.Any], t.Any]] = []    # хранение стека областей видимости (scopes)

    def register(
        self,
        interface: type[T],
        provider: t.Callable[..., T] | type[T],  # Функция принимает произвольное количество аргументов, фабрика
        lifestyle: LifeStyle = LifeStyle.PER_REQUEST,
        params: dict[str, t.Any] | None = None,) -> None:
        self._registrations[interface] = _Registration(provider, lifestyle, params)

    # Возвращает экземпляр зависимости для interface. В зависимости от lifestyle либо создает новый экземпляр (PER_REQUEST),
    # либо возвращает существующий экземпляр из SINGLETON или области видимости SCOPED.
    def get_instance(self, interface: type[T]) -> T:
        registration = self._registrations.get(interface)
        if registration is None:
            raise KeyError(f"Interface {interface} is not registration.")

        # Singleton
        if registration.lifestyle == LifeStyle.SINGLETON:
            if interface not in self._singletons:
                self._singletons[interface] = self._create(registration)
            return self._singletons[interface]

        # Scoped
        if registration.lifestyle == LifeStyle.SCOPED:
            if not self._scope_stack:   # Если он пуст,значит запрошенный scoped-сервис вне области видимости.
                raise RuntimeError("Scoped service requested outside the scope")
            scope = self._scope_stack[-1]  # получает последний элемент стека (текущую область видимости).
            if interface not in scope:
                scope[interface] = self._create(registration)
            return scope[interface]

        # PerRequest будет создаваться новый экземпляр, вне зависимости от того, сколько раз он был запрошен ранее.
        return self._create(registration)

     # Контекстный менеджер,создает и уничтожает области видимости.
    # добавляет словарь в _scope_stack при входе в область видимости и удаляет его при выходе.
    # позволяет управлять жизненным циклом SCOPED зависимостей.

    @contextmanager
    def create_scope(self):
        self._scope_stack.append({})
        try:
            yield self
        finally:
            self._scope_stack.pop()

    # Приватный метод создает экземпляр зависимости, используя provider и params из _Registration.
    # Если provider - класс,создает экземпляр класса,передавая параметры в конструктор.
    # Если provider - функция, вызывает эту функцию(фабрику).
    def _create(self, registration: _Registration):
        provider = registration.provider
        if callable(provider) and not isinstance(provider, type):
            # Это фабрика
            return provider()
        return provider(**registration.params)
