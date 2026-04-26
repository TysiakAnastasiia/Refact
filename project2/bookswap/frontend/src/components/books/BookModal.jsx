import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Book, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { booksApi, reviewsApi } from "../../api/client";
import useAuthStore from "../../store/authStore";
import StarRating from "../ui/StarRating";
import styles from "./BookModal.module.css";

const GENRE_LABELS = {
  fiction: "Проза",
  non_fiction: "Нон-фікшн",
  fantasy: "Фентезі",
  sci_fi: "Фантастика",
  mystery: "Детектив",
  romance: "Романтика",
  thriller: "Трилер",
  horror: "Жахи",
  biography: "Біографія",
  history: "Історія",
  science: "Наука",
  self_help: "Саморозвиток",
  children: "Дитяча",
  poetry: "Поезія",
  other: "Інше",
};

export default function BookModal({ book, onClose, onExchangeRequest }) {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [newRating, setNewRating] = useState(5);
  const [newReview, setNewReview] = useState("");
  const [showReviewForm, setShowReviewForm] = useState(false);

  const { data: reviews = [] } = useQuery({
    queryKey: ["book-reviews", book.id],
    queryFn: () => booksApi.getReviews(book.id).then((r) => r.data),
  });

  const createReview = useMutation({
    mutationFn: (data) => reviewsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(["book-reviews", book.id]);
      queryClient.invalidateQueries(["books"]);
      setNewReview("");
      setNewRating(5);
      setShowReviewForm(false);
    },
  });

  const deleteReview = useMutation({
    mutationFn: (id) => reviewsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(["book-reviews", book.id]);
      queryClient.invalidateQueries(["books"]);
    },
  });

  // Close on Escape
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const avgRating = reviews.length
    ? (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1)
    : null;

  const userReview = reviews.find((r) => r.user?.id === user?.id);

  const handleSubmitReview = (e) => {
    e.preventDefault();
    if (!newReview.trim()) return;
    createReview.mutate({
      book_id: book.id,
      rating: newRating,
      content: newReview,
    });
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Закрити"
        >
          ✕
        </button>

        {/* Top section */}
        <div className={styles.top}>
          <div className={styles.coverWrap}>
            {book.cover_url ? (
              <img
                src={book.cover_url}
                alt={book.title}
                className={styles.cover}
              />
            ) : (
              <div className={styles.coverFallback}>
                <Book className={styles.coverFallbackIcon} />
              </div>
            )}
          </div>

          <div className={styles.bookInfo}>
            <span className={styles.genre}>
              {GENRE_LABELS[book.genre] || book.genre}
            </span>
            <h2 className={styles.title}>{book.title}</h2>
            <p className={styles.author}>{book.author}</p>

            {book.published_year && (
              <span className={styles.year}>{book.published_year}</span>
            )}

            {avgRating && (
              <div className={styles.ratingRow}>
                <StarRating rating={parseFloat(avgRating)} size="md" />
                <span className={styles.ratingNum}>{avgRating}</span>
                <span className={styles.ratingCount}>
                  ({reviews.length} рецензій)
                </span>
              </div>
            )}

            {book.description && (
              <p className={styles.description}>{book.description}</p>
            )}

            <div className={styles.actions}>
              {book.is_available_for_exchange &&
                user &&
                book.owner_id !== user.id && (
                  <button
                    className={styles.exchangeBtn}
                    onClick={() => {
                      onExchangeRequest?.(book);
                      onClose();
                    }}
                  >
                    <RefreshCw className={styles.exchangeBtnIcon} />{" "}
                    Запропонувати обмін
                  </button>
                )}
              {user && !userReview && (
                <button
                  className={styles.reviewBtn}
                  onClick={() => setShowReviewForm((v) => !v)}
                >
                  ✍️ Написати рецензію
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Review form */}
        {showReviewForm && user && (
          <form className={styles.reviewForm} onSubmit={handleSubmitReview}>
            <h4 className={styles.reviewFormTitle}>Ваша рецензія</h4>
            <div className={styles.ratingPicker}>
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  className={`${styles.starBtn} ${n <= newRating ? styles.starActive : ""}`}
                  onClick={() => setNewRating(n)}
                >
                  ★
                </button>
              ))}
            </div>
            <textarea
              className={styles.reviewTextarea}
              value={newReview}
              onChange={(e) => setNewReview(e.target.value)}
              placeholder="Поділіться думками про книгу..."
              rows={4}
              required
            />
            <div className={styles.reviewFormActions}>
              <button
                type="button"
                className={styles.cancelBtn}
                onClick={() => setShowReviewForm(false)}
              >
                Скасувати
              </button>
              <button
                type="submit"
                className={styles.submitBtn}
                disabled={createReview.isPending}
              >
                {createReview.isPending ? "Публікація..." : "Опублікувати"}
              </button>
            </div>
          </form>
        )}

        {/* Reviews list */}
        <div className={styles.reviews}>
          <h3 className={styles.reviewsTitle}>
            Рецензії{" "}
            {reviews.length > 0 && (
              <span className={styles.reviewsCount}>{reviews.length}</span>
            )}
          </h3>

          {reviews.length === 0 ? (
            <p className={styles.noReviews}>
              Поки немає рецензій. Будьте першим!
            </p>
          ) : (
            <div className={styles.reviewList}>
              {reviews.map((review) => (
                <div key={review.id} className={styles.reviewItem}>
                  <div className={styles.reviewHeader}>
                    <div className={styles.reviewUser}>
                      <div className={styles.reviewAvatar}>
                        {review.user?.avatar_url ? (
                          <img src={review.user.avatar_url} alt="" />
                        ) : (
                          review.user?.username?.[0]?.toUpperCase()
                        )}
                      </div>
                      <div>
                        <span className={styles.reviewUsername}>
                          {review.user?.username}
                        </span>
                        <span className={styles.reviewDate}>
                          {new Date(review.created_at).toLocaleDateString(
                            "uk-UA"
                          )}
                        </span>
                      </div>
                    </div>
                    <div className={styles.reviewRight}>
                      <StarRating rating={review.rating} size="sm" />
                      {user?.id === review.user?.id && (
                        <button
                          className={styles.deleteReviewBtn}
                          onClick={() => deleteReview.mutate(review.id)}
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  </div>
                  {review.content && (
                    <p className={styles.reviewContent}>{review.content}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
