import { useState } from 'react';
import { Header } from '../components/Header';
import { HabitList } from '../components/HabitList';
import { AddHabit } from '../components/AddHabit';
import { useHabitStore } from '../store/habitStore';
import { useEffect } from 'react';

export function Habits() {
  const [showAddHabit, setShowAddHabit] = useState(false);
  const { fetchHabits, clearError } = useHabitStore();

  useEffect(() => {
    const userId = localStorage.getItem('user_id') || '1';
    fetchHabits(userId);
    clearError();
  }, [fetchHabits, clearError]);

  const handleAddHabit = () => {
    setShowAddHabit(true);
  };

  const handleCloseAddHabit = () => {
    setShowAddHabit(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onAddHabit={handleAddHabit} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Habits</h1>
          <p className="text-gray-600 mt-2">
            Track your daily and weekly habits to build consistency and achieve your goals.
          </p>
        </div>

        <HabitList />
      </main>

      {showAddHabit && (
        <AddHabit onClose={handleCloseAddHabit} />
      )}
    </div>
  );
}
