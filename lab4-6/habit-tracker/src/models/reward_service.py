from src.models.habit_log import HabitLog, LogStatus, Reward, RewardType
from src.patterns.observer import Observer


class RewardService(Observer):
    """
    Awards points to users when they complete habits.
    Implements Observer: reacts to habit completion events without tight coupling.
    """

    BASE_POINTS = 10.0

    def __init__(self):
        # user_id -> total points
        self._points: dict[str, float] = {}
        self._rewards_issued: list[Reward] = []

    def update(self, habit_log: HabitLog) -> None:
        if habit_log.status != LogStatus.COMPLETED:
            return

        reward = Reward(
            reward_type=RewardType.POINTS,
            value=self.BASE_POINTS,
            description=f"Completed habit {habit_log.habit_id}",
        )
        self._rewards_issued.append(reward)
        uid = habit_log.user_id
        self._points[uid] = self._points.get(uid, 0.0) + reward.get_value()

    def get_points(self, user_id: str) -> float:
        return self._points.get(user_id, 0.0)

    def get_rewards(self) -> list[Reward]:
        return list(self._rewards_issued)
