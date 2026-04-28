import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, X } from "lucide-react";
import { useState } from "react";
import { booksApi, exchangesApi } from "../../api/client";
import useAuthStore from "../../store/authStore";
import styles from "./ExchangeModal.module.css";

export default function ExchangeModal({ requestedBook, onClose }) {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [selectedBook, setSelectedBook] = useState(null);
  const [message, setMessage] = useState("");
  const [exchangeType, setExchangeType] = useState("chat"); // "book" or "chat"

  // Отримуємо книги користувача для пропозиції обміну
  const { data: userBooksData } = useQuery({
    queryKey: ["user-books", user?.id],
    queryFn: () => booksApi.list({ owner_id: user.id }).then((r) => r.data),
    enabled: !!user && exchangeType === "book",
  });

  const userBooks = userBooksData?.items || [];

  const createExchange = useMutation({
    mutationFn: (data) => {
      console.log("Creating exchange with data:", data);
      // Перевіряємо токен
      const stored = JSON.parse(localStorage.getItem("bookswap-auth") || "{}");
      const token = stored?.state?.accessToken;
      console.log("Token from storage:", token ? "exists" : "missing");
      return exchangesApi.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["exchanges"]);
      alert("✅ Запит на обмін надіслано!");
      onClose();
    },
    onError: (e) => {
      console.error("Error creating exchange:", e);
      console.error("Error response:", e.response?.data);
      console.error("Error status:", e.response?.status);
      alert(
        "❌ Помилка: " +
          (e.response?.data?.detail || e.message || "Спробуйте ще раз")
      );
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!user) {
      alert("Будь ласка, увійдіть в систему");
      return;
    }

    if (exchangeType === "book") {
      if (!selectedBook) {
        alert("Будь ласка, оберіть книгу для обміну");
        return;
      }
      // Обмін з вибраною книгою
      const exchangeData = {
        offered_book_id: selectedBook.id,
        requested_book_id: requestedBook.id,
      };
      console.log("Exchange data (with book):", exchangeData);
      console.log("Selected book:", selectedBook);
      console.log("Requested book:", requestedBook);
      createExchange.mutate(exchangeData);
    } else {
      // Обмін без книги - тільки повідомлення
      const exchangeDataNoBook = {
        offered_book_id: null,
        requested_book_id: requestedBook.id,
        message: message || "Хочу обмінятися, обговоримо деталі в чаті",
      };
      console.log("Exchange data (no book):", exchangeDataNoBook);
      console.log("Requested book:", requestedBook);
      createExchange.mutate(exchangeDataNoBook);
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h3>Запит на обмін</h3>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.requestedBook}>
            <h4>Книга, яку хочете отримати:</h4>
            <div className={styles.bookInfo}>
              <BookOpen className={styles.bookIcon} />
              <div>
                <strong>{requestedBook.title}</strong>
                <p>{requestedBook.author}</p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.exchangeOptions}>
              <h4>Оберіть варіант обміну:</h4>

              <label className={styles.option}>
                <input
                  type="radio"
                  name="exchangeType"
                  checked={exchangeType === "book"}
                  onChange={() => {
                    setExchangeType("book");
                    setSelectedBook(null);
                  }}
                />
                <div className={styles.optionContent}>
                  <strong>Обмінятися моєю книгою</strong>
                  <p>Пропонуйте конкретну книгу зі своєї колекції</p>
                </div>
              </label>

              <label className={styles.option}>
                <input
                  type="radio"
                  name="exchangeType"
                  checked={exchangeType === "chat"}
                  onChange={() => {
                    setExchangeType("chat");
                    setSelectedBook(null);
                  }}
                />
                <div className={styles.optionContent}>
                  <strong>Обговорити в чаті</strong>
                  <p>Немає книги для обміну? Обговоримо умови в повідомленні</p>
                </div>
              </label>
            </div>

            {exchangeType === "book" && (
              <div className={styles.bookSelection}>
                <h4>Оберіть книгу для обміну:</h4>
                {userBooks.length === 0 ? (
                  <p>
                    У вас ще немає книг. <a href="/catalog">Додати книгу</a>
                  </p>
                ) : (
                  <div className={styles.booksList}>
                    {userBooks.map((book) => (
                      <label key={book.id} className={styles.bookOption}>
                        <input
                          type="radio"
                          name="selectedBook"
                          checked={selectedBook?.id === book.id}
                          onChange={() => setSelectedBook(book)}
                        />
                        <div className={styles.bookOptionContent}>
                          <strong>{book.title}</strong>
                          <p>{book.author}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            )}

            {exchangeType === "chat" && (
              <div className={styles.messageSection}>
                <label htmlFor="message">Повідомлення власнику:</label>
                <textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Розкажіть, чому хочете обмінятися або які умови пропонуєте..."
                  rows={3}
                  className={styles.messageInput}
                />
              </div>
            )}

            <div className={styles.actions}>
              <button
                type="button"
                className={styles.cancelBtn}
                onClick={onClose}
              >
                Скасувати
              </button>
              <button
                type="submit"
                className={styles.submitBtn}
                disabled={createExchange.isPending}
              >
                {createExchange.isPending ? "Надсилання..." : "Надіслати запит"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
