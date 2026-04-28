import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Book, Edit, RefreshCw, Trash2 } from "lucide-react";
import { useState } from "react";
import { booksApi } from "../../api/client";
import useAuthStore from "../../store/authStore";
import StarRating from "../ui/StarRating";
import WishlistButton from "../ui/WishlistButton";
import styles from "./BookCard.module.css";
import BookModal from "./BookModal";
import EditBookModal from "./EditBookModal";

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
  console.log(
    "BookCard rendered with book:",
    book.title,
    "and onExchangeRequest:",
    !!onExchangeRequest
  );

  const [showModal, setShowModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  const isOwner = user && book.owner_id === user.id;

  const deleteBook = useMutation({
    mutationFn: () => booksApi.delete(book.id),
    onSuccess: () => {
      queryClient.invalidateQueries(["books"]);
      // Book will be removed from UI automatically due to cache invalidation
    },
    onError: (e) => {
      console.error("Error deleting book:", e);
      alert(
        "Помилка при видаленні книги: " +
          (e.response?.data?.detail || e.message)
      );
    },
  });

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
            {isOwner && (
              <div className={styles.ownerActions}>
                <button
                  className={styles.editBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowEditModal(true);
                  }}
                  title="Редагувати"
                >
                  <Edit size={14} />
                </button>
                <button
                  className={styles.deleteBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    if (
                      window.confirm(
                        "Ви впевнені, що хочете видалити цю книгу?"
                      )
                    ) {
                      deleteBook.mutate();
                    }
                  }}
                  title="Видалити"
                  disabled={deleteBook.isPending}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>
          {book.is_available_for_exchange && (
            <button
              className={styles.exchangeBtn}
              onClick={(e) => {
                console.log("Exchange button clicked for book:", book.title);
                console.log("Current user:", user);
                console.log("onExchangeRequest function:", !!onExchangeRequest);
                e.stopPropagation();
                onExchangeRequest?.(book);
              }}
              title="Запропонувати обмін"
            >
              <RefreshCw className={styles.exchangeBtnIcon} />
              Запропонувати обмін
            </button>
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
      {showEditModal && (
        <EditBookModal book={book} onClose={() => setShowEditModal(false)} />
      )}
    </>
  );
}
