// ─── ProfilePage.jsx ────────────────────────────────────────────────────────
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api/client'
import useAuthStore from '../store/authStore'
import StarRating from '../components/ui/StarRating'
import styles from './ProfilePage.module.css'

export default function ProfilePage() {
  const { userId } = useParams()
  const { user: currentUser } = useAuthStore()
  const queryClient = useQueryClient()
  const targetId = userId ? parseInt(userId) : currentUser?.id
  const isOwn = targetId === currentUser?.id

  const { data: profile } = useQuery({
    queryKey: ['user', targetId],
    queryFn: () => usersApi.getUser(targetId).then(r => r.data),
    enabled: !!targetId,
  })

  const { data: reviews = [] } = useQuery({
    queryKey: ['user-reviews', targetId],
    queryFn: () => usersApi.getUserReviews(targetId).then(r => r.data),
    enabled: !!targetId,
  })

  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})

  const updateProfile = useMutation({
    mutationFn: (data) => usersApi.updateMe(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['user', targetId])
      setEditing(false)
    },
  })

  if (!profile) return <div className={styles.loading}>Завантаження...</div>

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.avatarWrap}>
            {profile.avatar_url
              ? <img src={profile.avatar_url} alt="" className={styles.avatar} />
              : <div className={styles.avatarFallback}>{profile.username?.[0]?.toUpperCase()}</div>
            }
          </div>
          <div className={styles.headerInfo}>
            <h1 className={styles.username}>{profile.username}</h1>
            {profile.full_name && <p className={styles.fullName}>{profile.full_name}</p>}
            {profile.city && <p className={styles.city}>📍 {profile.city}</p>}
            {profile.bio && <p className={styles.bio}>{profile.bio}</p>}
            <p className={styles.joined}>
              Приєднався {new Date(profile.created_at).toLocaleDateString('uk-UA', { month: 'long', year: 'numeric' })}
            </p>
            {isOwn && (
              <button className={styles.editBtn} onClick={() => setEditing(true)}>
                ✏️ Редагувати профіль
              </button>
            )}
          </div>
          <div className={styles.stats}>
            <div className={styles.statItem}>
              <span className={styles.statNum}>{reviews.length}</span>
              <span className={styles.statLabel}>Рецензій</span>
            </div>
          </div>
        </div>

        {/* Reviews */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Рецензії</h2>
          {reviews.length === 0
            ? <p className={styles.empty}>Рецензій поки немає</p>
            : (
              <div className={styles.reviewList}>
                {reviews.map(r => (
                  <div key={r.id} className={styles.reviewCard}>
                    <div className={styles.reviewBook}>
                      <span className={styles.reviewBookTitle}>{r.book?.title}</span>
                      <span className={styles.reviewBookAuthor}>{r.book?.author}</span>
                    </div>
                    <StarRating rating={r.rating} size="sm" />
                    {r.content && <p className={styles.reviewContent}>{r.content}</p>}
                    <span className={styles.reviewDate}>{new Date(r.created_at).toLocaleDateString('uk-UA')}</span>
                  </div>
                ))}
              </div>
            )
          }
        </section>
      </div>
    </div>
  )
}

// fix: need useState import
import { useState } from 'react'
