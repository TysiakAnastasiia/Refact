// ─── ExchangePage.jsx ──────────────────────────────────────────────────────
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Book, MessageCircle, RefreshCw } from "lucide-react";
import { useState } from "react";
import { exchangesApi } from "../api/client";
import ChatWindow from "../components/chat/ChatWindow";
import useAuthStore from "../store/authStore";
import styles from "./ExchangePage.module.css";

const STATUS_LABELS = {
  pending: "Очікує",
  accepted: "Прийнято",
  completed: "Завершено",
  rejected: "Відхилено",
  cancelled: "Скасовано",
};
const STATUS_COLORS = {
  pending: "warning",
  accepted: "success",
  completed: "success",
  rejected: "error",
  cancelled: "muted",
};

export default function ExchangePage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState("all");
  const [activeChat, setActiveChat] = useState(null);

  const { data: allExchanges = [] } = useQuery({
    queryKey: ["exchanges", "all"],
    queryFn: () => exchangesApi.list().then((r) => r.data),
  });

  const { data: myExchanges = [] } = useQuery({
    queryKey: ["exchanges", "my"],
    queryFn: () => exchangesApi.myExchanges().then((r) => r.data),
    enabled: !!user,
  });

  const accept = useMutation({
    mutationFn: (id) => exchangesApi.accept(id),
    onSuccess: () => queryClient.invalidateQueries(["exchanges"]),
  });
  const reject = useMutation({
    mutationFn: (id) => exchangesApi.reject(id),
    onSuccess: () => queryClient.invalidateQueries(["exchanges"]),
  });
  const complete = useMutation({
    mutationFn: (id) => exchangesApi.complete(id),
    onSuccess: () => queryClient.invalidateQueries(["exchanges"]),
  });

  const exchanges = tab === "all" ? allExchanges : myExchanges;

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>Обмін книгами</h1>
        <p className={styles.subtitle}>
          Запропонуйте обмін, прийміть пропозицію, домовтеся в чаті
        </p>

        {user && (
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${tab === "all" ? styles.activeTab : ""}`}
              onClick={() => setTab("all")}
            >
              Всі пропозиції
            </button>
            <button
              className={`${styles.tab} ${tab === "my" ? styles.activeTab : ""}`}
              onClick={() => setTab("my")}
            >
              Мої обміни
            </button>
          </div>
        )}

        <div className={styles.list}>
          {exchanges.length === 0 && (
            <div className={styles.empty}>
              <RefreshCw className={styles.emptyIcon} />
              <p>Обмінів поки немає</p>
            </div>
          )}
          {exchanges.map((ex) => {
            const isMine = ex.requester?.id === user?.id;
            const isOwner = ex.owner?.id === user?.id;
            return (
              <div key={ex.id} className={styles.card}>
                <div className={styles.cardBooks}>
                  <div className={styles.bookThumb}>
                    {ex.offered_book?.cover_url ? (
                      <img src={ex.offered_book.cover_url} alt="" />
                    ) : (
                      <Book className={styles.bookThumbIcon} />
                    )}
                    <div className={styles.bookThumbInfo}>
                      <span className={styles.bookThumbTitle}>
                        {ex.offered_book?.title}
                      </span>
                      <span className={styles.bookThumbAuthor}>
                        {ex.offered_book?.author}
                      </span>
                      <span className={styles.bookThumbOwner}>
                        від @{ex.requester?.username}
                      </span>
                    </div>
                  </div>
                  <div className={styles.arrow}>⇄</div>
                  <div className={styles.bookThumb}>
                    {ex.requested_book?.cover_url ? (
                      <img src={ex.requested_book.cover_url} alt="" />
                    ) : (
                      <Book className={styles.bookThumbIcon} />
                    )}
                    <div className={styles.bookThumbInfo}>
                      <span className={styles.bookThumbTitle}>
                        {ex.requested_book?.title}
                      </span>
                      <span className={styles.bookThumbAuthor}>
                        {ex.requested_book?.author}
                      </span>
                      <span className={styles.bookThumbOwner}>
                        від @{ex.owner?.username}
                      </span>
                    </div>
                  </div>
                </div>
                {ex.message && (
                  <p className={styles.message}>&quot;{ex.message}&quot;</p>
                )}
                <div className={styles.cardFooter}>
                  <span
                    className={`${styles.status} ${styles[STATUS_COLORS[ex.status]]}`}
                  >
                    {STATUS_LABELS[ex.status]}
                  </span>
                  <div className={styles.cardActions}>
                    {isOwner && ex.status === "pending" && (
                      <>
                        <button
                          className={styles.acceptBtn}
                          onClick={() => accept.mutate(ex.id)}
                        >
                          ✓ Прийняти
                        </button>
                        <button
                          className={styles.rejectBtn}
                          onClick={() => reject.mutate(ex.id)}
                        >
                          ✕ Відхилити
                        </button>
                      </>
                    )}
                    {(isMine || isOwner) && ex.status === "accepted" && (
                      <button
                        className={styles.completeBtn}
                        onClick={() => complete.mutate(ex.id)}
                      >
                        ✓ Завершити
                      </button>
                    )}
                    {(isMine || isOwner) &&
                      ex.status !== "completed" &&
                      ex.status !== "rejected" && (
                        <button
                          className={styles.chatBtn}
                          onClick={() => setActiveChat(ex)}
                        >
                          <MessageCircle className={styles.chatBtnIcon} /> Чат
                        </button>
                      )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {activeChat && (
        <div className={styles.chatPanel}>
          <ChatWindow
            exchange={activeChat}
            onClose={() => setActiveChat(null)}
          />
        </div>
      )}
    </div>
  );
}
