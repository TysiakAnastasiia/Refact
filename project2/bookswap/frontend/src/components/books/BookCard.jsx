import { Book, RefreshCw } from "lucide-react";
import { useState } from "react";
import StarRating from "../ui/StarRating";
import WishlistButton from "../ui/WishlistButton";
import styles from "./BookCard.module.css";
import BookModal from "./BookModal";

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

const CONDITION_LABELS = {
  new: "Нова",
  good: "Добрий",
  fair: "Задовільний",
  poor: "Погано",
};

export default function BookCard({ book, onExchangeRequest }) {
  const [showModal, setShowModal] = useState(false);

  const coverFallback = (
    <div className={styles.coverFallback}>
      <Book className={styles.coverIcon} />
      <span className={styles.coverTitle}>{book.title}</span>
    </div>
  );

  return (
    <>
      <article className={styles.card} onClick={() => setShowModal(true)}>
        <div className={styles.coverWrap}>
          {book.cover_url ? (
            <img
              src={book.cover_url}
              alt={book.title}
              className={styles.cover}
            />
          ) : (
            coverFallback
          )}
          <div className={styles.coverOverlay}>
            <span className={styles.viewBtn}>Детальніше</span>
          </div>
          <div
            className={styles.topBadges}
            onClick={(e) => e.stopPropagation()}
          >
            <WishlistButton bookId={book.id} />
          </div>
          {book.is_available_for_exchange && (
            <span className={styles.exchangeBadge}>
              <RefreshCw className={styles.exchangeBadgeIcon} />{" "}
              <span>Обмін</span>
            </span>
          )}
        </div>

        <div className={styles.info}>
          <span className={styles.genre}>
            {GENRE_LABELS[book.genre] || book.genre}
          </span>
          <h3 className={styles.title}>{book.title}</h3>
          <p className={styles.author}>{book.author}</p>

          <div className={styles.meta}>
            <StarRating rating={book.average_rating} size="sm" />
            {book.review_count > 0 && (
              <span className={styles.reviewCount}>({book.review_count})</span>
            )}
          </div>

          <div className={styles.footer}>
            <span className={styles.condition}>
              {CONDITION_LABELS[book.condition]}
            </span>
            {book.owner && (
              <span className={styles.owner}>@{book.owner.username}</span>
            )}
          </div>
        </div>
      </article>

      {showModal && (
        <BookModal
          book={book}
          onClose={() => setShowModal(false)}
          onExchangeRequest={onExchangeRequest}
        />
      )}
    </>
  );
}
