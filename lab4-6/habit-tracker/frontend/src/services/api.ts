import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface User {
  id: string;
  name: string;
  email: string;
  points: number;
  level: number;
}

export interface Habit {
  id: string;
  name: string;
  description: string;
  type: "daily" | "weekly";
  frequency: number;
  points: number;
  streak: number;
  completed: boolean;
  created_at: string;
  user_id: string;
}

export interface HabitLog {
  id: string;
  habit_id: string;
  completed_at: string;
  points_earned: number;
}

export interface Reward {
  id: string;
  name: string;
  description: string;
  cost: number;
  category: string;
}

export interface CreateHabitRequest {
  name: string;
  description: string;
  type: "daily" | "weekly";
  frequency: number;
  points: number;
}

export interface UpdateHabitRequest {
  name?: string;
  description?: string;
  frequency?: number;
  points?: number;
}

class ApiService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
    },
  });

  constructor() {
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem("auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  async getUser(id: string): Promise<User> {
    const response = await this.api.get(`/users/${id}`);
    return response.data;
  }

  async updateUser(id: string, data: Partial<User>): Promise<User> {
    const response = await this.api.put(`/users/${id}`, data);
    return response.data;
  }

  async getHabits(userId: string): Promise<Habit[]> {
    const response = await this.api.get(`/users/${userId}/habits`);
    return response.data;
  }

  async getHabit(id: string): Promise<Habit> {
    const response = await this.api.get(`/habits/${id}`);
    return response.data;
  }

  async createHabit(userId: string, data: CreateHabitRequest): Promise<Habit> {
    const response = await this.api.post(`/users/${userId}/habits`, data);
    return response.data;
  }

  async updateHabit(id: string, data: UpdateHabitRequest): Promise<Habit> {
    const response = await this.api.put(`/habits/${id}`, data);
    return response.data;
  }

  async deleteHabit(id: string): Promise<void> {
    await this.api.delete(`/habits/${id}`);
  }

  async completeHabit(id: string): Promise<HabitLog> {
    const response = await this.api.post(`/habits/${id}/complete`);
    return response.data;
  }

  async getHabitLogs(habitId: string): Promise<HabitLog[]> {
    const response = await this.api.get(`/habits/${habitId}/logs`);
    return response.data;
  }

  async getRewards(): Promise<Reward[]> {
    const response = await this.api.get("/rewards");
    return response.data;
  }

  async redeemReward(
    userId: string,
    rewardId: string
  ): Promise<{ message: string }> {
    const response = await this.api.post(
      `/users/${userId}/rewards/${rewardId}/redeem`
    );
    return response.data;
  }

  async getUserStats(userId: string): Promise<{
    total_habits: number;
    completed_today: number;
    current_streak: number;
    total_points: number;
    weekly_progress: number;
  }> {
    const response = await this.api.get(`/users/${userId}/stats`);
    return response.data;
  }
}

export const apiService = new ApiService();
