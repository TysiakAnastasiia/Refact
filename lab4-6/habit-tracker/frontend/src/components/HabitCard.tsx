import { Calendar, Check, Flame, Trophy, X } from "lucide-react";
import type { Habit } from "../services/api";
import { useHabitStore } from "../store/habitStore";
import { Button } from "./ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/Card";

interface HabitCardProps {
  habit: Habit;
}

export function HabitCard({ habit }: HabitCardProps) {
  const { completeHabit, deleteHabit, loading } = useHabitStore();

  const handleComplete = async () => {
    if (!habit.completed) {
      await completeHabit(habit.id);
    }
  };

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this habit?")) {
      await deleteHabit(habit.id);
    }
  };

  return (
    <Card
      className={`transition-all duration-200 hover:shadow-md ${
        habit.completed ? "bg-green-50 border-green-200" : "bg-white"
      }`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle
              className={`text-lg ${
                habit.completed
                  ? "text-green-800 line-through"
                  : "text-gray-900"
              }`}
            >
              {habit.name}
            </CardTitle>
            <CardDescription className="mt-1">
              {habit.description}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2 ml-4">
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                habit.type === "daily"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-purple-100 text-purple-800"
              }`}
            >
              {habit.type}
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {habit.frequency}x/week
              </span>
            </div>

            <div className="flex items-center space-x-1">
              <Trophy className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium text-gray-700">
                {habit.points} pts
              </span>
            </div>

            {habit.streak > 0 && (
              <div className="flex items-center space-x-1">
                <Flame className="h-4 w-4 text-orange-500" />
                <span className="text-sm font-medium text-gray-700">
                  {habit.streak} day streak
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <Button
              onClick={handleComplete}
              disabled={habit.completed || loading}
              size="sm"
              variant={habit.completed ? "secondary" : "default"}
              className="flex items-center space-x-1"
            >
              {habit.completed ? (
                <>
                  <Check className="h-4 w-4" />
                  <span>Done</span>
                </>
              ) : (
                <>
                  <Check className="h-4 w-4" />
                  <span>Complete</span>
                </>
              )}
            </Button>

            <Button
              onClick={handleDelete}
              disabled={loading}
              size="sm"
              variant="destructive"
              className="p-2"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
