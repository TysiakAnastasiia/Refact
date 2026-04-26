// StarRating.jsx
import styles from './StarRating.module.css'

export default function StarRating({ rating, size = 'md', interactive = false, onRate }) {
  const stars = [1, 2, 3, 4, 5]

  return (
    <div className={`${styles.stars} ${styles[size]}`} aria-label={`Рейтинг: ${rating || 0} з 5`}>
      {stars.map(n => {
        const filled = rating && n <= Math.round(rating)
        return (
          <span
            key={n}
            className={`${styles.star} ${filled ? styles.filled : styles.empty} ${interactive ? styles.interactive : ''}`}
            onClick={interactive ? () => onRate?.(n) : undefined}
          >★</span>
        )
      })}
    </div>
  )
}
