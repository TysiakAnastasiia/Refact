import { useQuery } from "@tanstack/react-query";
import {
  Drama,
  FileText,
  Heart,
  Microscope,
  Rocket,
  Search,
  Sparkles,
  Sprout,
  User,
} from "lucide-react";
import { useState } from "react";
import { recommendationsApi } from "../api/client";
import styles from "./RecommendationsPage.module.css";

const GENRE_OPTIONS = [
  { value: "Фентезі", label: "Фентезі", icon: Drama },
  { value: "Наукова фантастика", label: "Фантастика", icon: Rocket },
  { value: "Детектив", label: "Детектив", icon: Search },
  { value: "Романтика", label: "Романтика", icon: Heart },
  { value: "Трилер", label: "Трилер" },
  { value: "Біографія", label: "Біографія", icon: User },
  { value: "Саморозвиток", label: "Саморозвиток", icon: Sprout },
  { value: "Наука", label: "Наука", icon: Microscope },
  { value: "Художня проза", label: "Проза", icon: FileText },
  { value: "Поезія", label: "Поезія", icon: Drama },
];

export default function RecommendationsPage() {
  const [selected, setSelected] = useState([]);
  const [shouldFetch, setShouldFetch] = useState(false);
  const [aiResponse, setAiResponse] = useState("");

  const {
    data: recs = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["recommendations", selected],
    queryFn: () => recommendationsApi.get(selected).then((r) => r.data),
    enabled: shouldFetch,
  });

  const toggleGenre = (val) => {
    setSelected((prev) =>
      prev.includes(val) ? prev.filter((g) => g !== val) : [...prev, val]
    );
    setShouldFetch(false);
  };

  const handleGet = () => {
    setShouldFetch(true);
    refetch();

    // Generate AI response
    const genresText =
      selected.length > 0 ? selected.join(", ") : "різні жанри";
    const response = `На основі ваших улюблених жанрів (${genresText}) я підібрав для вас чудові книги! 
    Кожна рекомендація враховує сучасні тренди та класичні твори, які точно вас зацікавлять. 
    Обирайте будь-яку книгу з пропозицій вище - кожна з них пройшла строгий відбір за критеріями якості та популярності серед читачів.`;
    setAiResponse(response);
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.hero}>
          <Sparkles className={styles.heroIcon} />
          <h1 className={styles.title}>AI-рекомендації</h1>
          <p className={styles.subtitle}>
            Оберіть улюблені жанри — і наш AI підбере книги саме для вас
          </p>
        </div>

        <div className={styles.genreGrid}>
          {GENRE_OPTIONS.map((g) => (
            <button
              key={g.value}
              className={`${styles.genreBtn} ${selected.includes(g.value) ? styles.selected : ""}`}
              onClick={() => toggleGenre(g.value)}
            >
              {g.label}
              {selected.includes(g.value) && (
                <span className={styles.check}>✓</span>
              )}
            </button>
          ))}
        </div>

        <div className={styles.actions}>
          <button
            className={styles.getBtn}
            onClick={handleGet}
            disabled={isLoading}
          >
            {isLoading
              ? "🤔 Обдумуємо рекомендації..."
              : "✨ Отримати рекомендації"}
          </button>
          {selected.length > 0 && (
            <p className={styles.selectedInfo}>
              Вибрано жанрів: {selected.length}
            </p>
          )}
        </div>

        {recs.length > 0 && (
          <div className={styles.results}>
            <h2 className={styles.resultsTitle}>Рекомендовано для вас</h2>
            <div className={styles.recGrid}>
              {recs.map((rec, i) => (
                <div key={i} className={styles.recCard}>
                  <div className={styles.recNum}>{i + 1}</div>
                  <div className={styles.recInfo}>
                    <h3 className={styles.recTitle}>{rec.title}</h3>
                    <p className={styles.recAuthor}>{rec.author}</p>
                    <span className={styles.recGenre}>{rec.genre}</span>
                    {rec.description && (
                      <p className={styles.recDescription}>{rec.description}</p>
                    )}
                    <p className={styles.recReason}>💡 {rec.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Response */}
        {aiResponse && (
          <div className={styles.aiResponse}>
            <h3 className={styles.aiResponseTitle}>💭 Відповідь AI</h3>
            <p className={styles.aiResponseText}>{aiResponse}</p>
          </div>
        )}
      </div>
    </div>
  );
}
