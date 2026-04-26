import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../api/client'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,

      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const { data } = await api.post('/auth/login', { email, password })
          set({ accessToken: data.access_token, refreshToken: data.refresh_token })
          const me = await api.get('/users/me')
          set({ user: me.data, isLoading: false })
          return { success: true }
        } catch (err) {
          set({ isLoading: false })
          return { success: false, error: err.response?.data?.detail || 'Login failed' }
        }
      },

      register: async (email, username, password, fullName) => {
        set({ isLoading: true })
        try {
          const { data } = await api.post('/auth/register', {
            email, username, password, full_name: fullName,
          })
          set({ accessToken: data.access_token, refreshToken: data.refresh_token })
          const me = await api.get('/users/me')
          set({ user: me.data, isLoading: false })
          return { success: true }
        } catch (err) {
          set({ isLoading: false })
          return { success: false, error: err.response?.data?.detail || 'Registration failed' }
        }
      },

      logout: () => set({ user: null, accessToken: null, refreshToken: null }),

      updateUser: (userData) => set({ user: { ...get().user, ...userData } }),
    }),
    {
      name: 'bookswap-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
)

export default useAuthStore
