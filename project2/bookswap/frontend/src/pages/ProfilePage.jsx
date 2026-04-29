// ─── ProfilePage.jsx ────────────────────────────────────────────────────────
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import { booksApi, exchangesApi, usersApi } from "../api/client";
import BookCard from "../components/books/BookCard";
import StarRating from "../components/ui/StarRating";
import useAuthStore from "../store/authStore";
import styles from "./ProfilePage.module.css";

export default function ProfilePage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuthStore();
  const queryClient = useQueryClient();
  const targetId = userId ? parseInt(userId) : currentUser?.id;
  const isOwn = targetId === currentUser?.id;

  const { data: profile } = useQuery({
    queryKey: ["user", targetId],
    queryFn: () => usersApi.getUser(targetId).then((r) => r.data),
    enabled: !!targetId,
  });

  const { data: reviews = [] } = useQuery({
    queryKey: ["user-reviews", targetId],
    queryFn: () => usersApi.getUserReviews(targetId).then((r) => r.data),
    enabled: !!targetId,
  });

  const { data: userBooks = [] } = useQuery({
    queryKey: ["user-books", targetId],
    queryFn: () => booksApi.list({ owner_id: targetId }).then((r) => r.data),
    enabled: !!targetId,
  });

  const { data: userExchanges = [] } = useQuery({
    queryKey: ["user-exchanges", targetId],
    queryFn: () =>
      exchangesApi
        .myExchanges()
        .then((r) =>
          r.data.filter(
            (e) => e.requester_id === targetId || e.owner_id === targetId
          )
        ),
    enabled: !!targetId,
  });

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [activeTab, setActiveTab] = useState("reviews");

  const updateProfile = useMutation({
    mutationFn: (data) => usersApi.updateMe(data),
    onSuccess: () => {
      queryClient.invalidateQueries(["user", targetId]);
      setEditing(false);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    updateProfile.mutate(form);
  };

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  if (!profile) return <div className={styles.loading}>Завантаження...</div>;

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.avatarWrap}>
            {profile.avatar_url ? (
              <img src={profile.avatar_url} alt="" className={styles.avatar} />
            ) : (
              <div className={styles.avatarFallback}>
                {profile.username?.[0]?.toUpperCase()}
              </div>
            )}
          </div>
          <div className={styles.headerInfo}>
            <h1 className={styles.username}>{profile.username}</h1>
            {profile.full_name && (
              <p className={styles.fullName}>{profile.full_name}</p>
            )}
            {profile.city && <p className={styles.city}>📍 {profile.city}</p>}
            {profile.bio && <p className={styles.bio}>{profile.bio}</p>}
            <p className={styles.joined}>
              Приєднався{" "}
              {new Date(profile.created_at).toLocaleDateString("uk-UA", {
                month: "long",
                year: "numeric",
              })}
            </p>
            {isOwn && !editing && (
              <button
                className={styles.editBtn}
                onClick={() => setEditing(true)}
              >
                ✏️ Редагувати профіль
              </button>
            )}
            {isOwn && editing && (
              <form className={styles.editForm} onSubmit={handleSubmit}>
                <div className={styles.formGroup}>
                  <label>Повне ім&apos;я</label>
                  <input
                    type="text"
                    value={form.full_name || profile.full_name || ""}
                    onChange={handleChange("full_name")}
                    className={styles.formInput}
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Про себе</label>
                  <textarea
                    value={form.bio || profile.bio || ""}
                    onChange={handleChange("bio")}
                    className={styles.formTextarea}
                    rows={3}
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Місто</label>
                  <input
                    type="text"
                    value={form.city || profile.city || ""}
                    onChange={handleChange("city")}
                    className={styles.formInput}
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>URL аватара</label>
                  <input
                    type="url"
                    value={form.avatar_url || profile.avatar_url || ""}
                    onChange={handleChange("avatar_url")}
                    className={styles.formInput}
                    placeholder="https://..."
                  />
                </div>
                <div className={styles.formActions}>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => setEditing(false)}
                  >
                    Скасувати
                  </button>
                  <button
                    type="submit"
                    className={styles.saveBtn}
                    disabled={updateProfile.isPending}
                  >
                    {updateProfile.isPending ? "Збереження..." : "Зберегти"}
                  </button>
                </div>
              </form>
            )}
          </div>
          <div className={styles.stats}>
            <div className={styles.statItem}>
              <span className={styles.statNum}>{reviews.length}</span>
              <span className={styles.statLabel}>Рецензій</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statNum}>4.8</span>
              <span className={styles.statLabel}>Оцінка</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statNum}>127</span>
              <span className={styles.statLabel}>Підписники</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statNum}>15</span>
              <span className={styles.statLabel}>Книг</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statNum}>8</span>
              <span className={styles.statLabel}>Обмінів</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <section className={styles.section}>
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${activeTab === "reviews" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("reviews")}
            >
              Рецензії ({reviews.length})
            </button>
            <button
              className={`${styles.tab} ${activeTab === "books" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("books")}
            >
              Книги ({userBooks.length})
            </button>
            <button
              className={`${styles.tab} ${activeTab === "exchanges" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("exchanges")}
            >
              Обміни ({userExchanges.length})
            </button>
          </div>

          {/* Reviews Tab */}
          {activeTab === "reviews" && (
            <div className={styles.tabContent}>
              {reviews.length === 0 ? (
                <p className={styles.empty}>Рецензій поки немає</p>
              ) : (
                <div className={styles.reviewList}>
                  {reviews.map((r) => (
                    <div key={r.id} className={styles.reviewCard}>
                      <div className={styles.reviewBook}>
                        <span className={styles.reviewBookTitle}>
                          {r.book?.title}
                        </span>
                        <span className={styles.reviewBookAuthor}>
                          {r.book?.author}
                        </span>
                      </div>
                      <StarRating rating={r.rating} size="sm" />
                      {r.content && (
                        <p className={styles.reviewContent}>{r.content}</p>
                      )}
                      <span className={styles.reviewDate}>
                        {new Date(r.created_at).toLocaleDateString("uk-UA")}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Books Tab */}
          {activeTab === "books" && (
            <div className={styles.tabContent}>
              {userBooks.length === 0 ? (
                <p className={styles.empty}>Книг поки немає</p>
              ) : (
                <div className={styles.booksGrid}>
                  {userBooks.map((book) => (
                    <BookCard key={book.id} book={book} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Exchanges Tab */}
          {activeTab === "exchanges" && (
            <div className={styles.tabContent}>
              {userExchanges.length === 0 ? (
                <p className={styles.empty}>Обмінів поки немає</p>
              ) : (
                <div className={styles.exchangesList}>
                  {userExchanges.map((exchange) => (
                    <div key={exchange.id} className={styles.exchangeCard}>
                      <div className={styles.exchangeInfo}>
                        <h4>Обмін #{exchange.id}</h4>
                        <p>
                          Статус:{" "}
                          <span className={styles.status}>
                            {exchange.status}
                          </span>
                        </p>
                        <p>
                          Запропоновано книга: {exchange.offered_book?.title}
                        </p>
                        <p>Запитана книга: {exchange.requested_book?.title}</p>
                        <p>
                          Дата:{" "}
                          {new Date(exchange.created_at).toLocaleDateString(
                            "uk-UA"
                          )}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

// fix: need useState import
