from src.models.habit_log import Reward, RewardType


class RewardDecorator(Reward):
    """
    Base decorator that wraps a Reward and delegates get_value().
    (Decorator pattern: dynamic behaviour extension without subclassing the original)
    """

    def __init__(self, wrapped: Reward):
        # Bypass dataclass __init__; copy fields from wrapped
        self.id = wrapped.id
        self.reward_type = wrapped.reward_type
        self.value = wrapped.value
        self.description = wrapped.description
        self._wrapped = wrapped

    def get_value(self) -> float:
        return self._wrapped.get_value()


class BonusRewardDecorator(RewardDecorator):
    """Adds a flat bonus on top of the base reward value."""

    def __init__(self, wrapped: Reward, bonus: float):
        super().__init__(wrapped)
        self._bonus = bonus

    def get_value(self) -> float:
        return super().get_value() + self._bonus


class MultiplierRewardDecorator(RewardDecorator):
    """Multiplies the reward value by a given factor."""

    def __init__(self, wrapped: Reward, multiplier: float):
        super().__init__(wrapped)
        self._multiplier = multiplier

    def get_value(self) -> float:
        return super().get_value() * self._multiplier
