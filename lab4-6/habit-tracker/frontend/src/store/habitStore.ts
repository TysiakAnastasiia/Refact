import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { CreateHabitRequest, Habit, Reward, User } from "../services/api";
import { apiService } from "../services/api";

interface HabitState {
  // State
  user: User | null;
  habits: Habit[];
  rewards: Reward[];
  loading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User) => void;
  fetchUser: (userId: string) => Promise<void>;
  fetchHabits: (userId: string) => Promise<void>;
  fetchRewards: () => Promise<void>;
  createHabit: (userId: string, habit: CreateHabitRequest) => Promise<void>;
  updateHabit: (
    habitId: string,
    data: Partial<CreateHabitRequest>
  ) => Promise<void>;
  deleteHabit: (habitId: string) => Promise<void>;
  completeHabit: (habitId: string) => Promise<void>;
  redeemReward: (userId: string, rewardId: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

// Mock data for demo
const mockUser: User = {
  id: "1",
  name: "John Doe",
  email: "john@example.com",
  points: 150,
  level: 3,
};

const mockHabits: Habit[] = [
  {
    id: "1",
    name: "Morning Exercise",
    description: "30 minutes of cardio workout",
    type: "daily",
    frequency: 1,
    points: 10,
    streak: 5,
    completed: false,
    created_at: "2024-01-01T00:00:00Z",
    user_id: "1",
  },
  {
    id: "2",
    name: "Read for 20 minutes",
    description: "Read a book or educational content",
    type: "daily",
    frequency: 1,
    points: 5,
    streak: 3,
    completed: true,
    created_at: "2024-01-02T00:00:00Z",
    user_id: "1",
  },
  {
    id: "3",
    name: "Meditation",
    description: "10 minutes of mindfulness meditation",
    type: "daily",
    frequency: 1,
    points: 8,
    streak: 7,
    completed: false,
    created_at: "2024-01-03T00:00:00Z",
    user_id: "1",
  },
  {
    id: "4",
    name: "Weekly Meal Prep",
    description: "Prepare healthy meals for the week",
    type: "weekly",
    frequency: 1,
    points: 20,
    streak: 2,
    completed: false,
    created_at: "2024-01-04T00:00:00Z",
    user_id: "1",
  },
  {
    id: "5",
    name: "Drink 8 glasses of water",
    description: "Stay hydrated throughout the day",
    type: "daily",
    frequency: 8,
    points: 6,
    streak: 12,
    completed: true,
    created_at: "2024-01-05T00:00:00Z",
    user_id: "1",
  },
  {
    id: "6",
    name: "Practice Guitar",
    description: "15 minutes of guitar practice",
    type: "daily",
    frequency: 1,
    points: 7,
    streak: 4,
    completed: false,
    created_at: "2024-01-06T00:00:00Z",
    user_id: "1",
  },
  {
    id: "7",
    name: "Write Journal",
    description: "Write about your thoughts and experiences",
    type: "daily",
    frequency: 1,
    points: 9,
    streak: 2,
    completed: false,
    created_at: "2024-01-07T00:00:00Z",
    user_id: "1",
  },
  {
    id: "8",
    name: "Weekly Review",
    description: "Review goals and plan for next week",
    type: "weekly",
    frequency: 1,
    points: 15,
    streak: 8,
    completed: false,
    created_at: "2024-01-08T00:00:00Z",
    user_id: "1",
  },
];

const mockRewards: Reward[] = [
  {
    id: "1",
    name: "Extra Break Time",
    description: "30 minutes of extra break time",
    cost: 50,
    category: "time",
  },
  {
    id: "2",
    name: "Movie Night",
    description: "Watch a movie without guilt",
    cost: 100,
    category: "entertainment",
  },
  {
    id: "3",
    name: "Coffee Treat",
    description: "Enjoy your favorite coffee drink",
    cost: 25,
    category: "food",
  },
  {
    id: "4",
    name: "Gaming Session",
    description: "1 hour of guilt-free gaming",
    cost: 75,
    category: "entertainment",
  },
  {
    id: "5",
    name: "Book Purchase",
    description: "Buy a new book of your choice",
    cost: 150,
    category: "education",
  },
  {
    id: "6",
    name: "Spa Day",
    description: "Relaxing spa treatment or massage",
    cost: 200,
    category: "wellness",
  },
];

export const useHabitStore = create<HabitState>()(
  devtools(
    (set, get) => ({
      // Initial state with mock data
      user: mockUser,
      habits: mockHabits,
      rewards: mockRewards,
      loading: false,
      error: null,

      // Actions
      setUser: (user) => set({ user }),

      fetchUser: async (userId) => {
        set({ loading: true, error: null });
        try {
          // For demo, use mock data without API
          set({ user: mockUser, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to fetch user",
            loading: false,
          });
        }
      },

      fetchHabits: async (userId) => {
        set({ loading: true, error: null });
        try {
          // For demo, use mock data without API
          set({ habits: mockHabits, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to fetch habits",
            loading: false,
          });
        }
      },

      fetchRewards: async () => {
        set({ loading: true, error: null });
        try {
          // For demo, use mock data without API
          // const rewards = await apiService.getRewards();
          set({ rewards: mockRewards, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : "Failed to fetch rewards",
            loading: false,
          });
        }
      },

      createHabit: async (userId, habit) => {
        set({ loading: true, error: null });
        try {
          // For demo, create habit locally without API
          const newHabit: Habit = {
            id: Date.now().toString(),
            ...habit,
            streak: 0,
            completed: false,
            created_at: new Date().toISOString(),
            user_id: userId,
          };
          set((state) => ({
            habits: [...state.habits, newHabit],
            loading: false,
          }));
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to create habit",
            loading: false,
          });
        }
      },

      updateHabit: async (habitId, data) => {
        set({ loading: true, error: null });
        try {
          const updatedHabit = await apiService.updateHabit(habitId, data);
          set((state) => ({
            habits: state.habits.map((h) =>
              h.id === habitId ? updatedHabit : h
            ),
            loading: false,
          }));
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to update habit",
            loading: false,
          });
        }
      },

      completeHabit: async (habitId) => {
        set({ loading: true, error: null });
        try {
          await apiService.completeHabit(habitId);
          set((state) => ({
            habits: state.habits.map((h) =>
              h.id === habitId
                ? { ...h, completed: true, streak: h.streak + 1 }
                : h
            ),
            loading: false,
          }));
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : "Failed to complete habit",
            loading: false,
          });
        }
      },

      redeemReward: async (userId, rewardId) => {
        set({ loading: true, error: null });
        try {
          await apiService.redeemReward(userId, rewardId);
          // Refresh user data to update points
          await get().fetchUser(userId);
          set({ loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : "Failed to redeem reward",
            loading: false,
          });
        }
      },

      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
    }),
    {
      name: "habit-store",
    }
  )
);
