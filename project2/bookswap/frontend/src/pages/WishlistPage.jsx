// WishlistPage.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { wishlistApi } from '../api/client'
import BookCard from '../components/books/BookCard'
import styles from './WishlistPage.module.css'

export default function WishlistPage() {
  const queryClient = useQueryClient()
  const { data: items = [], isLoading } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => wishlistApi.get().then(r => r.data),
  })

  const remove = useMutation({
    mutationFn: (bookId) => wishlistApi.remove(bookId),
    onSuccess: () => queryClient.invalidateQueries(['wishlist']),
  })

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1 className={styles.title}>Список бажань</h1>
          <span className={styles.count}>{items.length} книг</span>
        </div>

        {isLoading ? (
          <p className={styles.loading}>Завантаження...</p>
        ) : items.length === 0 ? (
          <div className={styles.empty}>
            <span>♡</span>
            <p>Ваш список бажань порожній</p>
            <p className={styles.emptySub}>Додайте книги, які хочете прочитати або отримати в обмін</p>
          </div>
        ) : (
          <div className={styles.grid}>
            {items.map(item => (
              <BookCard key={item.id} book={item.book} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
