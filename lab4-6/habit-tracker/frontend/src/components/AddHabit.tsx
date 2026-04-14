import { Calendar, Target, X } from "lucide-react";
import { useState } from "react";
import type { CreateHabitRequest } from "../services/api";
import { useHabitStore } from "../store/habitStore";
import { Button } from "./ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/Card";

interface AddHabitProps {
  onClose: () => void;
}

export function AddHabit({ onClose }: AddHabitProps) {
  const { createHabit, loading, error } = useHabitStore();
  const [formData, setFormData] = useState<CreateHabitRequest>({
    name: "",
    description: "",
    type: "daily",
    frequency: 1,
    points: 10,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const userId = localStorage.getItem("user_id") || "1";

    await createHabit(userId, formData);
    if (!error) {
      onClose();
    }
  };

  const handleChange = (
    field: keyof CreateHabitRequest,
    value: string | number
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md bg-white shadow-2xl border-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-primary" />
              <CardTitle>Add New Habit</CardTitle>
            </div>
            <Button onClick={onClose} variant="ghost" size="sm" className="p-1">
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>
            Create a new habit to track and build consistency
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Habit Name
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="e.g., Morning Exercise"
                required
              />
            </div>

            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange("description", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="e.g., 30 minutes of cardio workout"
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="type"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Type
                </label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) => handleChange("type", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="frequency"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Frequency
                </label>
                <input
                  type="number"
                  id="frequency"
                  value={formData.frequency}
                  onChange={(e) =>
                    handleChange("frequency", parseInt(e.target.value))
                  }
                  min="1"
                  max="7"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="points"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Points per Completion
              </label>
              <input
                type="number"
                id="points"
                value={formData.points}
                onChange={(e) =>
                  handleChange("points", parseInt(e.target.value))
                }
                min="1"
                max="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <Button
                type="button"
                onClick={onClose}
                variant="outline"
                className="flex-1"
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" className="flex-1" disabled={loading}>
                {loading ? "Creating..." : "Create Habit"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
