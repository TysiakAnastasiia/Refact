import { useState } from "react";
import { booksApi } from "../../api/client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Sparkles, ThumbsUp, FileText, AlertTriangle, RefreshCw } from "lucide-react";
import styles from "./AddBookModal.module.css";

const GENRES = [
  { value: "fiction", label: "Проза" },
  { value: "non_fiction", label: "Нон-фікшн" },
  { value: "fantasy", label: "Фентезі" },
  { value: "sci_fi", label: "Фантастика" },
  { value: "mystery", label: "Детектив" },
  { value: "romance", label: "Романтика" },
  { value: "thriller", label: "Трилер" },
  { value: "horror", label: "Жахи" },
  { value: "biography", label: "Біографія" },
  { value: "history", label: "Історія" },
  { value: "science", label: "Наука" },
  { value: "self_help", label: "Саморозвиток" },
  { value: "children", label: "Дитяча" },
  { value: "poetry", label: "Поезія" },
  { value: "other", label: "Інше" },
];

const CONDITIONS = [
  { value: "new", label: "Нова", icon: Sparkles },
  { value: "good", label: "Добрий стан", icon: ThumbsUp },
  { value: "fair", label: "Задовільний", icon: FileText },
  { value: "poor", label: "Поганий", icon: AlertTriangle },
];

export default function EditBookModal({ book, onClose }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    title: book.title || "",
    author: book.author || "",
    description: book.description || "",
    isbn: book.isbn || "",
    cover_url: book.cover_url || "",
    genre: book.genre || "fiction",
    published_year: book.published_year || "",
    language: book.language || "Ukrainian",
    condition: book.condition || "good",
    is_available_for_exchange: book.is_available_for_exchange || true,
  });
  const [error, setError] = useState("");

  const updateBook = useMutation({
    mutationFn: (data) => booksApi.update(book.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(["books"]);
      onClose();
    },
    onError: (e) => {
      console.log("Full error object:", e);
      console.log("Error response data:", e.response?.data);
      let errorMessage = "Помилка при оновленні";
      try {
        if (e.response?.data?.detail) {
          console.log("Error detail:", e.response.data.detail);
          if (typeof e.response.data.detail === "string") {
            errorMessage = e.response.data.detail;
          } else if (Array.isArray(e.response.data.detail)) {
            errorMessage = e.response.data.detail
              .map((err) => err.msg || err)
              .join(", ");
          } else {
            errorMessage = JSON.stringify(e.response.data.detail);
          }
        } else if (e.response?.data?.message) {
          errorMessage = e.response.data.message;
        } else if (e.message) {
          errorMessage = e.message;
        }
      } catch (parseError) {
        console.log("Error parsing error object:", parseError);
        errorMessage = "Помилка валідації даних";
      }
      const finalMessage =
        typeof errorMessage === "string"
          ? errorMessage
          : "Помилка при оновленні";
      console.log("Final error message:", finalMessage);
      setError(finalMessage);
    },
  });

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    const payload = {
      ...form,
      published_year: form.published_year
        ? parseInt(form.published_year)
        : null,
      // Clean up empty strings to null for optional fields
      description: form.description || null,
      isbn: form.isbn || null,
      cover_url: form.cover_url || null,
    };
    console.log("Updating book with payload:", payload);
    updateBook.mutate(payload);
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>Редагувати книгу</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            ✕
          </button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.label}>Назва *</label>
              <input
                className={styles.input}
                value={form.title}
                onChange={set("title")}
                required
                placeholder="Назва книги"
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Автор *</label>
              <input
                className={styles.input}
                value={form.author}
                onChange={set("author")}
                required
                placeholder="Ім'я автора"
              />
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Опис</label>
            <textarea
              className={styles.textarea}
              value={form.description}
              onChange={set("description")}
              placeholder="Короткий опис книги..."
              rows={3}
            />
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.label}>Жанр *</label>
              <select
                className={styles.select}
                value={form.genre}
                onChange={set("genre")}
                required
              >
                {GENRES.map((g) => (
                  <option key={g.value} value={g.value}>
                    {g.label}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Рік видання</label>
              <input
                className={styles.input}
                type="number"
                value={form.published_year}
                onChange={set("published_year")}
                placeholder="2024"
                min="1000"
                max="2100"
              />
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.label}>ISBN</label>
              <input
                className={styles.input}
                value={form.isbn}
                onChange={set("isbn")}
                placeholder="978-0-123456-78-9"
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Мова</label>
              <select
                className={styles.select}
                value={form.language}
                onChange={set("language")}
              >
                <option value="Ukrainian">Українська</option>
                <option value="English">English</option>
                <option value="Polish">Polski</option>
                <option value="Russian">Русский</option>
              </select>
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Стан *</label>
            <select
              className={styles.select}
              value={form.condition}
              onChange={set("condition")}
              required
            >
              {CONDITIONS.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>URL обкладинки</label>
            <input
              className={styles.input}
              value={form.cover_url}
              onChange={set("cover_url")}
              placeholder="https://..."
            />
          </div>

          <div className={styles.field}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={form.is_available_for_exchange}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    is_available_for_exchange: e.target.checked,
                  }))
                }
              />
              <span>
                Доступна для обміну{" "}
                <RefreshCw className={styles.toggleIcon} />
              </span>
            </label>
          </div>

          {error && (
            <p className={styles.error}>
              {typeof error === "string" ? error : JSON.stringify(error)}
            </p>
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
              disabled={updateBook.isPending}
            >
              {updateBook.isPending ? "Збереження..." : "Зберегти"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
