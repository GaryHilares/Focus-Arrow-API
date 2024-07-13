from abc import ABC, abstractmethod
from string import ascii_lowercase, ascii_uppercase, digits
import random


class AbstractTokenGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        raise NotImplementedError


class RandomTokenGenerator(AbstractTokenGenerator):
    def generate_pin() -> str:
        return "".join(
            [
                random.choice(ascii_lowercase + ascii_uppercase + digits)
                for _ in range(8)
            ]
        )
