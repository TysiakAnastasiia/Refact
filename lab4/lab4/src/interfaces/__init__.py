from abc import ABC, abstractmethod


class IObserver(ABC):

    @abstractmethod
    def update(self, order) -> None:
        pass


class ISubject(ABC):

    @abstractmethod
    def attach(self, observer: IObserver) -> None:
        pass

    @abstractmethod
    def detach(self, observer: IObserver) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class IOrderFactory(ABC):

    @abstractmethod
    def create_order(self, customer, dishes: list):
        pass


class IDatabase(ABC):

    @abstractmethod
    def save_order(self, order) -> None:
        pass

    @abstractmethod
    def get_all_orders(self) -> list:
        pass
