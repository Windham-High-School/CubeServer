""" For managing derived property values in AutoEncodable objects

This allows you to specify a property method like so

class MyModel(object):

    ...

    def __init__(self):
        self.deriver = DerivedFieldManager()

    @property
    @self.deriver.derived_property
    def my_derived_property(self):
        return self.my_property + 1

And then the value of my_derived_property will be automatically encoded
and decoded along with the rest of the object, re-evaluated upon
deriver.eval(), which for convenience is called automatically upon encoding.

This is useful for properties that are derived from other properties
and are not otherwise stored in the database, but might have benefits
when it comes to querying or other operations.
"""

from typing import Callable, Any


class DerivedFieldManager:
    """ Manages specific property methods, caching them in the object
    until eval() is called
    """

    def __init__(self) -> None:
        self.__property_methods: list[Callable[[], Any]] = []
        self.__property_cache: dict[str, Any] = {}

    def __getattribute__(self, __name: str) -> Any:
        if __name in self.__property_cache.keys():
            return self.__property_cache[__name]
        return super().__getattribute__(__name)

    def derived_property(
        self,
        func: Callable[[], Any],
        cache: bool
    ) -> Callable[[], Any]:
        """ Decorator for a derived property method
        @param func: The property method to decorate
        @param cache: False force re-evaluates the property instead of
                       using the cached value
        """
        self.__property_methods.append(func)
        def wrapper():
            if not cache or \
            func.__name__ not in self.__property_cache.keys():
                self.__property_cache[func.__name__] = func()
            return self.__property_cache[func.__name__]
        return wrapper

    def init_property(self, name: str, value: Any) -> None:
        """ Initializes a property to a value
        """
        self.__property_cache[name] = value

    def eval(self) -> None:
        """ Re-evaluates all cached properties
        """
        for func in self.__property_methods:
            self.__property_cache[func.__name__] = func()

    def clear(self) -> None:
        """ Clears all cached properties
        """
        self.__property_cache = {}

    def __repr__(self) -> str:
        return f"DerivedFieldManager({self.__property_cache})"
