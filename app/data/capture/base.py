from abc import ABC, abstractmethod
from typing import Iterable

from app.data.models.candle import Candle


class CandleCapture(ABC):

    @abstractmethod
    def fetch(
        self,
        symbol: str,
        limit: int = 100,
    ) -> Iterable[Candle]:
        """
        Provider-independent capture contract.

        Real providers are implemented later.
        """
        raise NotImplementedError
