import { BarChart3, Plus, Target, Trophy } from "lucide-react";
import { useHabitStore } from "../store/habitStore";
import { Button } from "./ui/Button";

interface HeaderProps {
  onAddHabit: () => void;
}

export function Header({ onAddHabit }: HeaderProps) {
  const { user } = useHabitStore();

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <Target className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">Habit Tracker</h1>
              <p className="text-sm text-gray-500">
                Build better habits, one day at a time
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            {user && (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 bg-primary-50 px-3 py-1 rounded-full">
                  <Trophy className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-primary">
                    {user.points} pts
                  </span>
                </div>
                <div className="flex items-center space-x-2 bg-secondary-50 px-3 py-1 rounded-full">
                  <BarChart3 className="h-4 w-4 text-secondary" />
                  <span className="text-sm font-medium text-secondary">
                    Level {user.level}
                  </span>
                </div>
              </div>
            )}

            <Button
              onClick={onAddHabit}
              className="flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>Add Habit</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
