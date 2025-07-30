from abc import ABC, abstractmethod

class AbstractSingleton(ABC):
    _instance = None
    _initialized = False  # Flag to track if the instance has been initialized

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AbstractSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not type(self)._initialized:
            # Only initialize once
            self._initialize()
            type(self)._initialized = True

    @abstractmethod
    def _initialize(self):
        """Method for initialization logic, must be implemented by the subclass."""
        pass

    @abstractmethod
    def some_method(self):
        """Abstract method that must be implemented by any subclass."""
        pass

# Concrete Singleton Class
class ConcreteSingleton(AbstractSingleton):
    def _initialize(self):
        self.value = 42  # Custom initialization logic for the singleton instance

    def some_method(self):
        return f"Concrete implementation of some_method. Value: {self.value}"

# Testing the Abstract Singleton
singleton1 = ConcreteSingleton()
singleton2 = ConcreteSingleton()

print(singleton1 is singleton2)  # Output: True (both are the same instance)
print(singleton1.some_method())  # Output: Concrete implementation of some_method. Value: 42

# Modifying the singleton's value from one reference
singleton1.value = 99
print(singleton2.some_method())  # Output: Concrete implementation of some_method. Value: 99
