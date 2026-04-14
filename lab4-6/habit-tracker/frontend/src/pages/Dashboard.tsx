import { Calendar, Flame, Target, TrendingUp, Trophy } from "lucide-react";
import { useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";
import { useHabitStore } from "../store/habitStore";

export function Dashboard() {
  const { user, habits, fetchUser, fetchHabits } = useHabitStore();

  useEffect(() => {
    const userId = localStorage.getItem("user_id") || "1";
    fetchUser(userId);
    fetchHabits(userId);
  }, [fetchUser, fetchHabits]);

  const todayCompleted = habits.filter((h) => h.completed).length;
  const todayTotal = habits.length;
  const totalPoints = habits.reduce(
    (sum, h) => sum + (h.completed ? h.points : 0),
    0
  );
  const activeStreaks = habits.filter((h) => h.streak > 0).length;

  const stats = [
    {
      title: "Today's Progress",
      value: `${todayCompleted}/${todayTotal}`,
      description: "Habits completed today",
      icon: Target,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "Total Points",
      value: user?.points || 0,
      description: "Points earned all time",
      icon: Trophy,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
    },
    {
      title: "Active Streaks",
      value: activeStreaks,
      description: "Habits with current streaks",
      icon: Flame,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
    {
      title: "Current Level",
      value: user?.level || 1,
      description: "Your current level",
      icon: TrendingUp,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
  ];

  const recentHabits = habits.slice(0, 5);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back! Here's your progress overview.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-md ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5" />
              <span>Recent Habits</span>
            </CardTitle>
            <CardDescription>Your most recent habit activities</CardDescription>
          </CardHeader>
          <CardContent>
            {recentHabits.length > 0 ? (
              <div className="space-y-3">
                {recentHabits.map((habit) => (
                  <div
                    key={habit.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">
                        {habit.name}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {habit.description}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {habit.completed && (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          Completed
                        </span>
                      )}
                      <span className="text-sm font-medium text-gray-600">
                        {habit.points} pts
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No habits yet
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Start by creating your first habit
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Daily Goal</h4>
                <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${todayTotal > 0 ? (todayCompleted / todayTotal) * 100 : 0}%`,
                    }}
                  ></div>
                </div>
                <p className="text-sm text-blue-700">
                  {todayCompleted} of {todayTotal} habits completed today
                </p>
              </div>

              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Keep it up!</h4>
                <p className="text-sm text-green-700">
                  You're doing great! Consistency is key to building lasting
                  habits.
                </p>
              </div>

              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-2">Pro Tip</h4>
                <p className="text-sm text-purple-700">
                  Start small and gradually increase difficulty. Small wins lead
                  to big changes!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
