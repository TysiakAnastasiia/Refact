import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import useAuthStore from './store/authStore'
import Layout from './components/ui/Layout'
import HomePage from './pages/HomePage'
import CatalogPage from './pages/CatalogPage'
import ExchangePage from './pages/ExchangePage'
import ProfilePage from './pages/ProfilePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import WishlistPage from './pages/WishlistPage'
import RecommendationsPage from './pages/RecommendationsPage'
import './styles/globals.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 1000 * 60 * 2, retry: 1 },
  },
})

function PrivateRoute({ children }) {
  const { accessToken } = useAuthStore()
  return accessToken ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="catalog" element={<CatalogPage />} />
            <Route path="exchange" element={<ExchangePage />} />
            <Route path="wishlist" element={<PrivateRoute><WishlistPage /></PrivateRoute>} />
            <Route path="recommendations" element={<PrivateRoute><RecommendationsPage /></PrivateRoute>} />
            <Route path="profile/:userId?" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
