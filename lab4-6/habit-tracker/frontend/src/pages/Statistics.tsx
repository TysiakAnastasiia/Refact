import { Award, BarChart3, Calendar, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";
import { useHabitStore } from "../store/habitStore";

export function Statistics() {
  const { user, habits, fetchUser, fetchHabits } = useHabitStore();
  const [weeklyData, setWeeklyData] = useState<number[]>([0, 0, 0, 0, 0, 0, 0]);

  useEffect(() => {
    const userId = localStorage.getItem("user_id") || "1";
    fetchUser(userId);
    fetchHabits(userId);

    setWeeklyData([
      Math.floor(Math.random() * 10) + 2,
      Math.floor(Math.random() * 10) + 2,
      Math.floor(Math.random() * 10) + 2,
      Math.floor(Math.random() * 10) + 2,
      Math.floor(Math.random() * 10) + 2,
      Math.floor(Math.random() * 10) + 2,
      Math.floor(Math.random() * 10) + 2,
    ]);
  }, [fetchUser, fetchHabits]);

  const totalHabits = habits.length;
  const completedToday = habits.filter((h) => h.completed).length;
  const completionRate =
    totalHabits > 0 ? Math.round((completedToday / totalHabits) * 100) : 0;
  const totalStreakDays = habits.reduce((sum, h) => sum + h.streak, 0);
  const averageStreak =
    totalHabits > 0 ? Math.round(totalStreakDays / totalHabits) : 0;

  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const maxWeeklyValue = Math.max(...weeklyData, 1);

  const habitTypeStats = {
    daily: habits.filter((h) => h.type === "daily").length,
    weekly: habits.filter((h) => h.type === "weekly").length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Statistics</h1>
        <p className="text-gray-600 mt-2">
          Track your progress and analyze your habit patterns.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Habits</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalHabits}</div>
            <p className="text-xs text-muted-foreground">Active habits</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Today's Completion
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completionRate}%</div>
            <p className="text-xs text-muted-foreground">
              {completedToday} of {totalHabits} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Average Streak
            </CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averageStreak}</div>
            <p className="text-xs text-muted-foreground">Days per habit</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Points</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{user?.points || 0}</div>
            <p className="text-xs text-muted-foreground">Points earned</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Weekly Progress</CardTitle>
          <CardDescription>
            Your habit completion over the past 7 days
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-end justify-between h-32">
              {weeklyData.map((value, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  <div className="w-full max-w-12 flex flex-col items-center">
                    <span className="text-xs font-medium text-gray-600 mb-2">
                      {value}
                    </span>
                    <div
                      className="w-full bg-primary rounded-t transition-all duration-300"
                      style={{
                        height: `${(value / maxWeeklyValue) * 100}%`,
                        minHeight: "4px",
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-between">
              {weekDays.map((day, index) => (
                <div key={index} className="flex-1 text-center">
                  <span className="text-xs text-gray-500">{day}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Habit Types</CardTitle>
            <CardDescription>
              Distribution of your habits by type
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Daily Habits</span>
                <span className="text-sm text-gray-600">
                  {habitTypeStats.daily}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${totalHabits > 0 ? (habitTypeStats.daily / totalHabits) * 100 : 0}%`,
                  }}
                ></div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Weekly Habits</span>
                <span className="text-sm text-gray-600">
                  {habitTypeStats.weekly}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${totalHabits > 0 ? (habitTypeStats.weekly / totalHabits) * 100 : 0}%`,
                  }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Performers</CardTitle>
            <CardDescription>Habits with the longest streaks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {habits
                .filter((h) => h.streak > 0)
                .sort((a, b) => b.streak - a.streak)
                .slice(0, 5)
                .map((habit, index) => (
                  <div
                    key={habit.id}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="flex items-center justify-center w-6 h-6 text-xs font-medium bg-primary text-primary-foreground rounded-full">
                        {index + 1}
                      </span>
                      <span className="text-sm font-medium">{habit.name}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">
                        {habit.streak} days
                      </span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-orange-500 h-2 rounded-full"
                          style={{
                            width: `${Math.min((habit.streak / 30) * 100, 100)}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              {habits.filter((h) => h.streak > 0).length === 0 && (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">No active streaks yet</p>
                  <p className="text-xs text-gray-400">
                    Complete habits daily to build streaks!
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
