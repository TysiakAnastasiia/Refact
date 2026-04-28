//
// HomePage.jsx
//
import { useQuery } from "@tanstack/react-query";
import { Book } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { booksApi } from "../api/client";
import BookCard from "../components/books/BookCard";
import ExchangeModal from "../components/exchanges/ExchangeModal";
import useAuthStore from "../store/authStore";
import styles from "./HomePage.module.css";

export default function HomePage() {
  const { user } = useAuthStore();
  const [showExchangeModal, setShowExchangeModal] = useState(false);
  const [selectedBookForExchange, setSelectedBookForExchange] = useState(null);

  const { data } = useQuery({
    queryKey: ["books", "recent"],
    queryFn: () => booksApi.list({ page: 1, page_size: 6 }).then((r) => r.data),
  });

  const handleExchangeRequest = (book) => {
    console.log("HomePage handleExchangeRequest called with book:", book);
    if (!user) {
      alert("Будь ласка, увійдіть в систему");
      return;
    }
    if (book.owner_id === user.id) {
      alert("Ви не можете обмінятися власною книгою");
      return;
    }
    setSelectedBookForExchange(book);
    setShowExchangeModal(true);
  };

  const { data: exchangeData } = useQuery({
    queryKey: ["books", "exchange"],
    queryFn: () =>
      booksApi.list({ available_only: true, page_size: 4 }).then((r) => r.data),
  });

  return (
    <div className={styles.page}>
      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <span className={styles.heroTag}>
            <Book className={styles.heroTagIcon} /> Спільнота читачів
          </span>
          <h1 className={styles.heroTitle}>
            Діліться книгами,
            <br />
            <em>відкривайте нові світи</em>
          </h1>
          <p className={styles.heroSub}>
            Обмінюйтесь книгами з іншими читачами, залишайте рецензії та
            отримуйте персональні AI-рекомендації
          </p>
          <div className={styles.heroBtns}>
            <Link to="/catalog" className={styles.btnPrimary}>
              Переглянути каталог
            </Link>
            <Link to="/exchange" className={styles.btnSecondary}>
              Обмін книгами
            </Link>
          </div>
        </div>
        <div className={styles.heroDecor}>
          <div className={styles.heroBook}>
            <img
              src="/src/styles/img.jpg"
              alt="Book decoration"
              className={styles.heroBookImage}
            />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statNum}>{data?.total ?? "—"}</span>
          <span className={styles.statLabel}>Книг у каталозі</span>
        </div>
        <div className={styles.statDivider} />
        <div className={styles.stat}>
          <span className={styles.statNum}>{exchangeData?.total ?? "—"}</span>
          <span className={styles.statLabel}>Доступні для обміну</span>
        </div>
        <div className={styles.statDivider} />
        <div className={styles.stat}>
          <span className={styles.statNum}>✨</span>
          <span className={styles.statLabel}>AI-рекомендації</span>
        </div>
      </section>

      {/* Recent books */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Нові надходження</h2>
          <Link to="/catalog" className={styles.seeAll}>
            Всі книги →
          </Link>
        </div>
        <div className={styles.booksGrid}>
          {data?.items?.map((book) => (
            <BookCard
              key={book.id}
              book={book}
              onExchangeRequest={handleExchangeRequest}
            />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className={styles.cta}>
        <div className={styles.ctaContent}>
          <h2 className={styles.ctaTitle}>✨ Отримайте AI-рекомендації</h2>
          <p className={styles.ctaSub}>
            Наш AI аналізує ваші вподобання і пропонує книги саме для вас
          </p>
          <Link to="/recommendations" className={styles.ctaBtn}>
            Спробувати зараз
          </Link>
        </div>
      </section>

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
