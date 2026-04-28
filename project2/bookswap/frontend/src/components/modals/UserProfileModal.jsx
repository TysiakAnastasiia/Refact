import { X, Mail, MapPin, Calendar, Book, Star } from "lucide-react";
import styles from "./UserProfileModal.module.css";

export default function UserProfileModal({ user, onClose }) {
  if (!user) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Профіль користувача</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className={styles.profileContent}>
          <div className={styles.profileHeader}>
            <div className={styles.avatar}>
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.username} />
              ) : (
                <div className={styles.avatarPlaceholder}>
                  {user.username?.charAt(0)?.toUpperCase()}
                </div>
              )}
            </div>
            <div className={styles.profileInfo}>
              <h3>{user.full_name || user.username}</h3>
              <p className={styles.username}>@{user.username}</p>
              {user.city && (
                <p className={styles.location}>
                  <MapPin size={14} />
                  {user.city}
                </p>
              )}
            </div>
          </div>

          {user.bio && (
            <div className={styles.bioSection}>
              <h4>Про себе</h4>
              <p>{user.bio}</p>
            </div>
          )}

          <div className={styles.statsSection}>
            <h4>Статистика</h4>
            <div className={styles.statsGrid}>
              <div className={styles.statCard}>
                <Book size={16} />
                <span>{user.book_count || 0}</span>
                <p>Книг</p>
              </div>
              <div className={styles.statCard}>
                <Star size={16} />
                <span>{user.review_count || 0}</span>
                <p>Рецензій</p>
              </div>
              <div className={styles.statCard}>
                <Calendar size={16} />
                <span>
                  {new Date(user.created_at).toLocaleDateString("uk-UA")}
                </span>
                <p>На сайті</p>
              </div>
            </div>
          </div>

          <div className={styles.contactSection}>
            <h4>Контакти</h4>
            <div className={styles.contactInfo}>
              <p>
                <Mail size={14} />
                {user.email}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
