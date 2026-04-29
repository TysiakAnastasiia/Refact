import axios from "axios";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

// Request interceptor — attach token
api.interceptors.request.use((config) => {
  try {
    const stored = JSON.parse(localStorage.getItem("bookswap-auth") || "{}");
    const token = stored?.state?.accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (error) {
    // Ignore invalid stored auth data.
    void error;
  }
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("bookswap-auth");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;

//  API methods

export const booksApi = {
  list: (params) => api.get("/books", { params }),
  get: (id) => api.get(`/books/${id}`),
  create: (data) => api.post("/books", data),
  update: (id, data) => api.patch(`/books/${id}`, data),
  delete: (id) => api.delete(`/books/${id}`),
  getReviews: (id, params) => api.get(`/books/${id}/reviews`, { params }),
};

export const reviewsApi = {
  create: (data) => api.post("/reviews", data),
  update: (id, data) => api.patch(`/reviews/${id}`, data),
  delete: (id) => api.delete(`/reviews/${id}`),
};

export const exchangesApi = {
  list: (params) => api.get("/exchanges", { params }),
  myExchanges: () => api.get("/exchanges/my"),
  getBetweenUsers: (userId1, userId2) =>
    api.get("/exchanges/between", {
      params: { user1: userId1, user2: userId2 },
    }),
  create: (data) => api.post("/exchanges", data),
  accept: (id) => api.patch(`/exchanges/${id}/accept`),
  reject: (id) => api.patch(`/exchanges/${id}/reject`),
  complete: (id) => api.patch(`/exchanges/${id}/complete`),
};

export const wishlistApi = {
  get: () => api.get("/wishlist"),
  add: (bookId) => api.post(`/wishlist/${bookId}`),
  remove: (bookId) => api.delete(`/wishlist/${bookId}`),
};

export const chatApi = {
  getMessages: (exchangeId) => api.get(`/chat/${exchangeId}`),
  send: (exchangeId, content) => api.post(`/chat/${exchangeId}`, { content }),
};

export const usersApi = {
  getMe: () => api.get("/users/me"),
  updateMe: (data) => api.patch("/users/me", data),
  getUser: (id) => api.get(`/users/${id}`),
  getUserReviews: (id) => api.get(`/users/${id}/reviews`),
  search: (query) => api.get("/users/search", { params: { q: query } }),
};

export const recommendationsApi = {
  get: (genres) =>
    api.get("/recommendations", { params: { genres: genres?.join(",") } }),
};

export const friendsApi = {
  add: (userId) => api.post(`/friends/${userId}`),
  get: () => api.get("/friends"),
};
