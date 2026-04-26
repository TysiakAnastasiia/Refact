import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { wishlistApi } from '../../api/client'
import useAuthStore from '../../store/authStore'
import styles from './WishlistButton.module.css'

export default function WishlistButton({ bookId }) {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [optimistic, setOptimistic] = useState(null)

  const { data: wishlist = [] } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => wishlistApi.get().then(r => r.data),
    enabled: !!user,
  })

  const isInWishlist = optimistic !== null
    ? optimistic
    : wishlist.some(item => item.book?.id === bookId)

  const add = useMutation({
    mutationFn: () => wishlistApi.add(bookId),
    onMutate: () => setOptimistic(true),
    onSuccess: () => { queryClient.invalidateQueries(['wishlist']); setOptimistic(null) },
    onError: () => setOptimistic(null),
  })

  const remove = useMutation({
    mutationFn: () => wishlistApi.remove(bookId),
    onMutate: () => setOptimistic(false),
    onSuccess: () => { queryClient.invalidateQueries(['wishlist']); setOptimistic(null) },
    onError: () => setOptimistic(null),
  })

  if (!user) return null

  const handleClick = (e) => {
    e.stopPropagation()
    isInWishlist ? remove.mutate() : add.mutate()
  }

  return (
    <button
      className={`${styles.btn} ${isInWishlist ? styles.active : ''}`}
      onClick={handleClick}
      aria-label={isInWishlist ? 'Видалити з бажань' : 'Додати до бажань'}
      title={isInWishlist ? 'Видалити з бажань' : 'Додати до бажань'}
    >
      {isInWishlist ? '♥' : '♡'}
    </button>
  )
}
