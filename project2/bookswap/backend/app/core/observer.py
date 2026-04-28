"""
Observer Pattern Implementation
Defines a one-to-many dependency between objects so that when one object changes state,
all its dependents are notified and updated automatically.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
from enum import Enum
import asyncio
from datetime import datetime


class EventType(Enum):
    """Types of events that can be observed."""
    USER_REGISTERED = "user_registered"
    BOOK_CREATED = "book_created"
    BOOK_EXCHANGED = "book_exchanged"
    EXCHANGE_CREATED = "exchange_created"
    EXCHANGE_ACCEPTED = "exchange_accepted"
    EXCHANGE_COMPLETED = "exchange_completed"
    MESSAGE_SENT = "message_sent"
    FRIEND_ADDED = "friend_added"
    REVIEW_CREATED = "review_created"


class Event:
    """Event object that contains event data."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any], timestamp: datetime = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_type': self.event_type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class Observer(ABC):
    """Abstract observer interface."""
    
    @abstractmethod
    async def update(self, event: Event) -> None:
        """Handle event notification."""
        pass


class Subject(ABC):
    """Abstract subject interface."""
    
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject."""
        pass
    
    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject."""
        pass
    
    @abstractmethod
    async def notify(self, event: Event) -> None:
        """Notify all observers about an event."""
        pass


class EventManager(Subject):
    """
    Concrete implementation of Subject using Observer pattern.
    Manages event notifications to multiple observers.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    async def notify(self, event: Event) -> None:
        """Notify all observers about an event."""
        # Add to history
        self._event_history.append(event)
        
        # Limit history size
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Notify all observers
        tasks = []
        for observer in self._observers:
            try:
                task = asyncio.create_task(observer.update(event))
                tasks.append(task)
            except Exception as e:
                print(f"Error notifying observer: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type."""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:] if limit > 0 else events
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()


class LoggingObserver(Observer):
    """Observer that logs events."""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = log_level
    
    async def update(self, event: Event) -> None:
        """Log event information."""
        print(f"[{self.log_level}] Event: {event.event_type.value} at {event.timestamp}")
        if event.data:
            print(f"  Data: {event.data}")


class StatisticsObserver(Observer):
    """Observer that tracks event statistics."""
    
    def __init__(self):
        self._event_counts: Dict[EventType, int] = {}
        self._total_events = 0
    
    async def update(self, event: Event) -> None:
        """Update event statistics."""
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1
        self._total_events += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics."""
        return {
            'total_events': self._total_events,
            'event_counts': {k.value: v for k, v in self._event_counts.items()},
            'last_updated': datetime.utcnow().isoformat()
        }


class WebSocketObserver(Observer):
    """Observer that sends events to WebSocket clients."""
    
    def __init__(self):
        self._connected_clients: List[Any] = []
    
    def add_client(self, client: Any) -> None:
        """Add a WebSocket client."""
        if client not in self._connected_clients:
            self._connected_clients.append(client)
    
    def remove_client(self, client: Any) -> None:
        """Remove a WebSocket client."""
        if client in self._connected_clients:
            self._connected_clients.remove(client)
    
    async def update(self, event: Event) -> None:
        """Send event to all connected WebSocket clients."""
        if not self._connected_clients:
            return
        
        message = {
            'type': 'event',
            'event': event.to_dict()
        }
        
        # Send to all clients (implementation depends on WebSocket library)
        for client in self._connected_clients[:]:  # Copy to avoid modification during iteration
            try:
                # This would be implemented based on your WebSocket library
                # await client.send_json(message)
                pass
            except Exception as e:
                print(f"Error sending to WebSocket client: {e}")
                # Remove disconnected client
                self._connected_clients.remove(client)


class EmailNotificationObserver(Observer):
    """Observer that sends email notifications for important events."""
    
    def __init__(self):
        self._notification_events = {
            EventType.EXCHANGE_ACCEPTED,
            EventType.EXCHANGE_COMPLETED,
            EventType.MESSAGE_SENT,
            EventType.FRIEND_ADDED,
        }
    
    async def update(self, event: Event) -> None:
        """Send email notification for important events."""
        if event.event_type not in self._notification_events:
            return
        
        # Extract user information from event data
        user_id = event.data.get('user_id')
        user_email = event.data.get('user_email')
        
        if not user_email:
            return
        
        # This would integrate with an email service
        print(f"Email notification to {user_email}: {event.event_type.value}")
        # await email_service.send_notification(user_email, event)


# Global event manager instance
event_manager = EventManager()

# Register default observers
event_manager.attach(LoggingObserver())
event_manager.attach(StatisticsObserver())
event_manager.attach(WebSocketObserver())
event_manager.attach(EmailNotificationObserver())
