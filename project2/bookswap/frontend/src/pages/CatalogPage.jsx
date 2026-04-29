import { useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Search } from "lucide-react";
import { useState } from "react";
import { booksApi } from "../api/client";
import AddBookModal from "../components/books/AddBookModal";
import BookCard from "../components/books/BookCard";
import ExchangeModal from "../components/exchanges/ExchangeModal";
import useAuthStore from "../store/authStore";
import styles from "./CatalogPage.module.css";

const GENRES = [
  { value: "", label: "Всі жанри" },
  { value: "fiction", label: "Проза" },
  { value: "non_fiction", label: "Нон-фікшн" },
  { value: "fantasy", label: "Фентезі" },
  { value: "sci_fi", label: "Фантастика" },
  { value: "mystery", label: "Детектив" },
  { value: "romance", label: "Романтика" },
  { value: "thriller", label: "Трилер" },
  { value: "biography", label: "Біографія" },
  { value: "history", label: "Історія" },
  { value: "science", label: "Наука" },
  { value: "self_help", label: "Саморозвиток" },
  { value: "poetry", label: "Поезія" },
];

export default function CatalogPage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [availableOnly, setAvailableOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [showAddBook, setShowAddBook] = useState(false);
  const [showExchangeModal, setShowExchangeModal] = useState(false);
  const [selectedBookForExchange, setSelectedBookForExchange] = useState(null);
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Отримуємо книги користувача для пропозиції обміну
  const { data: userBooks = [] } = useQuery({
    queryKey: ["user-books", user?.id],
    queryFn: () => booksApi.list({ owner_id: user.id }).then((r) => r.data),
    enabled: !!user,
  });

  const handleExchangeRequest = (book) => {
    console.log("handleExchangeRequest called with book:", book);
    console.log("Current user:", user);

    if (!user) {
      console.log("No user - showing alert");
      alert("Будь ласка, увійдіть в систему");
      return;
    }
    if (book.owner_id === user.id) {
      console.log("User owns the book - showing alert");
      alert("Ви не можете обмінятися власною книгою");
      return;
    }

    console.log("Setting selected book and showing modal");
    setSelectedBookForExchange(book);
    setShowExchangeModal(true);

    console.log("Modal state after setting:", {
      selectedBookForExchange: book,
      showExchangeModal: true,
    });
  };

  // Debounce search
  const handleSearchChange = (val) => {
    setSearch(val);
    clearTimeout(window._searchTimer);
    window._searchTimer = setTimeout(() => {
      setDebouncedSearch(val);
      setPage(1);
    }, 400);
  };

  const { data, isLoading } = useQuery({
    queryKey: ["books", debouncedSearch, genre, availableOnly, page],
    queryFn: () =>
      booksApi
        .list({
          q: debouncedSearch || undefined,
          genre: genre || undefined,
          available_only: availableOnly || undefined,
          page,
          page_size: 20,
        })
        .then((r) => r.data),
    keepPreviousData: true,
  });

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Header */}
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>Каталог книг</h1>
            <p className={styles.subtitle}>
              {data?.total !== undefined
                ? `${data.total} книг знайдено`
                : "Завантаження..."}
            </p>
          </div>
          {user && (
            <button
              className={styles.addBtn}
              onClick={() => setShowAddBook(true)}
            >
              + Додати книгу
            </button>
          )}
        </div>

        {/* Filters */}
        <div className={styles.filters}>
          <div className={styles.searchWrap}>
            <Search className={styles.searchIcon} />
            <input
              className={styles.searchInput}
              placeholder="Пошук за назвою або автором..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
            />
            {search && (
              <button
                className={styles.clearSearch}
                onClick={() => handleSearchChange("")}
              >
                ✕
              </button>
            )}
          </div>

          <div className={styles.genreScroll}>
            {GENRES.map((g) => (
              <button
                key={g.value}
                className={`${styles.genreChip} ${genre === g.value ? styles.activeChip : ""}`}
                onClick={() => {
                  setGenre(g.value);
                  setPage(1);
                }}
              >
                {g.label}
              </button>
            ))}
          </div>

          <label className={styles.toggle}>
            <input
              type="checkbox"
              checked={availableOnly}
              onChange={(e) => {
                setAvailableOnly(e.target.checked);
                setPage(1);
              }}
            />
            <span className={styles.toggleLabel}>
              Тільки доступні для обміну{" "}
              <RefreshCw className={styles.toggleIcon} />
            </span>
          </label>
        </div>

        {/* Grid */}
        {isLoading ? (
          <div className={styles.loading}>
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className={styles.skeleton} />
            ))}
          </div>
        ) : data?.items?.length === 0 ? (
          <div className={styles.empty}>
            <span className={styles.emptyIcon}>📭</span>
            <p>Нічого не знайдено. Спробуйте інший пошук.</p>
          </div>
        ) : (
          <div className={styles.grid}>
            {data?.items?.map((book) => {
              console.log(
                "Rendering BookCard for:",
                book.title,
                "with handleExchangeRequest:",
                !!handleExchangeRequest
              );
              return (
                <BookCard
                  key={book.id}
                  book={book}
                  onExchangeRequest={handleExchangeRequest}
                />
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {data?.pages > 1 && (
          <div className={styles.pagination}>
            <button
              className={styles.pageBtn}
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              ← Назад
            </button>
            <span className={styles.pageInfo}>
              {page} / {data.pages}
            </span>
            <button
              className={styles.pageBtn}
              disabled={page === data.pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Вперед →
            </button>
          </div>
        )}
      </div>

      {showAddBook && <AddBookModal onClose={() => setShowAddBook(false)} />}
      {showExchangeModal && selectedBookForExchange && (
        <ExchangeModal
          requestedBook={selectedBookForExchange}
          onClose={() => {
            setShowExchangeModal(false);
            setSelectedBookForExchange(null);
          }}
        />
      )}
    </div>
  );
}
