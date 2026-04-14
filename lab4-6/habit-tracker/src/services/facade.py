from typing import List, Optional
from datetime import date

from src.models.user import User
from src.models.habit import Habit, DailyHabit, WeeklyHabit
from src.models.habit_log import HabitLog, LogStatus
from src.repositories.repositories import (
    IHabitRepository, 
    IUserRepository, 
    IHabitLogRepository,
    HabitRepository,
    UserRepository,
    HabitLogRepository
)
from src.patterns.factory import HabitFactory, ConcreteHabitFactory
from src.patterns.observer import Observer, Observable, NotificationService, AnalyticsService
from src.models.reward_service import RewardService


class HabitServiceFacade:
    """
    Facade pattern implementation that provides a simplified interface
    to the complex habit tracking system.
    
    This class follows the Facade pattern to hide complexity and provide
    a clean API for habit management operations.
    """
    
    def __init__(self, 
                 habit_repo: Optional[IHabitRepository] = None,
                 user_repo: Optional[IUserRepository] = None,
                 log_repo: Optional[IHabitLogRepository] = None,
                 habit_factory: Optional[HabitFactory] = None):
        """
        Initialize the facade with repositories and factory.
        Uses singleton instances if not provided.
        """
        self.habit_repo = habit_repo or HabitRepository()
        self.user_repo = user_repo or UserRepository()
        self.log_repo = log_repo or HabitLogRepository()
        self.habit_factory = habit_factory or ConcreteHabitFactory()
        
        # Set up observer pattern
        self.observable = Observable()
        self._notification_service = NotificationService()
        self._analytics_service = AnalyticsService()
        self._reward_service = RewardService()
        
        self.observable.add_observer(self._notification_service)
        self.observable.add_observer(self._analytics_service)
        self.observable.add_observer(self._reward_service)
    
    def create_user(self, name: str, email: str) -> User:
        """
        Create a new user.
        
        Args:
            name: User name
            email: User email
            
        Returns:
            Created user object
        """
        user = User(name=name, email=email)
        self.user_repo.save(user)
        return user
    
    def register_user(self, name: str, email: str) -> User:
        """
        Register a new user (alias for create_user for test compatibility).
        
        Args:
            name: User name
            email: User email
            
        Returns:
            Created user object
        """
        return self.create_user(name, email)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        return self.user_repo.find_by_id(user_id)
    
    def create_habit(self, title: str, description: str, user_id: str, 
                    habit_type: str = "daily", **kwargs) -> Habit:
        """
        Create a new habit for a user.
        
        Args:
            title: Habit title
            description: Habit description
            user_id: User ID
            habit_type: Type of habit (daily, weekly, custom)
            **kwargs: Additional parameters for specific habit types
            
        Returns:
            Created habit object
        """
        # Check if user exists
        if not self.user_repo.find_by_id(user_id):
            raise ValueError("User not found")
        
        if not title or not title.strip():
            raise ValueError("Habit title cannot be empty")
        
        habit = self.habit_factory.create_habit(
            title=title.strip(),
            description=description,
            user_id=user_id,
            habit_type=habit_type,
            **kwargs
        )
        
        self.habit_repo.save(habit)
        return habit
    
    def get_user_habits(self, user_id: str) -> List[Habit]:
        """
        Get all habits for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user's habits
        """
        return self.habit_repo.find_by_user(user_id)
    
    def complete_habit(self, habit_id: str, completion_date: date = None) -> bool:
        """
        Mark a habit as completed.
        
        Args:
            habit_id: Habit ID
            completion_date: Date of completion (defaults to today)
            
        Returns:
            True if successful, False otherwise
        """
        habit = self.habit_repo.find_by_id(habit_id)
        if not habit:
            return False
        
        completion_date = completion_date or date.today()
        
        # Create habit log
        habit_log = HabitLog(
            habit_id=habit_id,
            user_id=habit.user_id,
            log_date=completion_date,
            status=LogStatus.COMPLETED
        )
        
        self.log_repo.save(habit_log)
        
        # Notify observers
        self.observable.notify_observers(habit_log)
        
        return True
    
    def mark_habit_done(self, habit_id: str, user_id: str, completion_date: date = None) -> HabitLog:
        """
        Mark habit as done (alias for complete_habit for test compatibility).
        
        Args:
            habit_id: Habit ID
            user_id: User ID
            completion_date: Date of completion
            
        Returns:
            Created habit log
        """
        habit = self.habit_repo.find_by_id(habit_id)
        if not habit:
            raise ValueError("Habit not found")
        
        completion_date = completion_date or date.today()
        
        habit_log = HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            log_date=completion_date,
            status=LogStatus.COMPLETED
        )
        
        self.log_repo.save(habit_log)
        self.observable.notify_observers(habit_log)
        
        return habit_log
    
    def delete_habit(self, habit_id: str) -> bool:
        """
        Delete a habit.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            True if successful, False otherwise
        """
        habit = self.habit_repo.find_by_id(habit_id)
        if not habit:
            return False
        
        self.habit_repo.delete(habit_id)
        return True
    
    def get_habit_completion_stats(self, habit_id: str) -> dict:
        """
        Get completion statistics for a habit.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            Dictionary with completion statistics
        """
        logs = self.log_repo.find_by_habit(habit_id)
        completed_logs = [log for log in logs if log.status == LogStatus.COMPLETED]
        
        return {
            'total_completions': len(completed_logs),
            'analytics_count': self.analytics_service.get_count(habit_id),
            'last_notification': self.notification_service.last_message()
        }
    
    def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List of all users
        """
        return self.user_repo.find_all()
    
    def get_all_habits(self) -> List[Habit]:
        """
        Get all habits.
        
        Returns:
            List of all habits
        """
        return self.habit_repo.find_all()
    
    def get_due_habits(self, user_id: str, check_date: date = None) -> List[Habit]:
        """
        Get habits that are due for a user on a specific date.
        
        Args:
            user_id: User ID
            check_date: Date to check (defaults to today)
            
        Returns:
            List of due habits
        """
        check_date = check_date or date.today()
        user_habits = self.get_user_habits(user_id)
        
        return [habit for habit in user_habits if habit.is_due(check_date)]
    
    def get_habit(self, habit_id: str) -> Optional[Habit]:
        """
        Get habit by ID.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            Habit object or None if not found
        """
        return self.habit_repo.find_by_id(habit_id)
    
    def get_streak(self, habit_id: str) -> int:
        """
        Get current streak for a habit.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            Current streak count
        """
        # Simple implementation - count consecutive completions
        logs = self.log_repo.find_by_habit(habit_id)
        completed_logs = sorted([log for log in logs if log.status == LogStatus.COMPLETED], 
                              key=lambda x: x.log_date, reverse=True)
        
        if not completed_logs:
            return 0
        
        streak = 1
        for i in range(1, len(completed_logs)):
            prev_date = completed_logs[i-1].log_date
            curr_date = completed_logs[i].log_date
            
            # Check if dates are consecutive
            if (prev_date - curr_date).days == 1:
                streak += 1
            else:
                break
        
        return streak
    
    def get_user_stats(self, user_id: str) -> dict:
        """
        Get user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
        """
        habits = self.get_user_habits(user_id)
        total_habits = len(habits)
        
        total_completions = 0
        total_points = 0
        for habit in habits:
            logs = self.log_repo.find_by_habit(habit.id)
            completed_logs = [log for log in logs if log.status == LogStatus.COMPLETED]
            total_completions += len(completed_logs)
            # Simple points calculation - 10 points per completion
            total_points += len(completed_logs) * 10
        
        return {
            'total_habits': total_habits,
            'total_completions': total_completions,
            'total_points': total_points,
            'completion_rate': total_completions / total_habits if total_habits > 0 else 0
        }
    
    @property
    def notification_service(self):
        """Get notification service for test access."""
        return self._notification_service
    
    @property  
    def analytics_service(self):
        """Get analytics service for test access."""
        return self._analytics_service
    
    @property
    def reward_service(self):
        """Get reward service for test access."""
        return self._reward_service
