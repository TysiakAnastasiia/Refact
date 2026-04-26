import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { chatApi } from "../../api/client";
import useAuthStore from "../../store/authStore";
import styles from "./ChatWindow.module.css";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

export default function ChatWindow({ exchange, onClose }) {
  const { user, accessToken } = useAuthStore();
  const queryClient = useQueryClient();
  const [input, setInput] = useState("");
  const [wsMessages, setWsMessages] = useState([]);
  const bottomRef = useRef(null);
  const wsRef = useRef(null);

  const { data: messages = [] } = useQuery({
    queryKey: ["chat", exchange.id],
    queryFn: () => chatApi.getMessages(exchange.id).then((r) => r.data),
  });

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket(
      `${WS_URL}/chat/${exchange.id}?token=${accessToken}`
    );
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "message") {
        setWsMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            sender: { id: data.sender_id },
            content: data.content,
            created_at: new Date().toISOString(),
            is_ws: true,
          },
        ]);
      }
    };

    return () => ws.close();
  }, [exchange.id, accessToken]);

  const sendMessage = useMutation({
    mutationFn: (content) => chatApi.send(exchange.id, content),
    onSuccess: () => {
      queryClient.invalidateQueries(["chat", exchange.id]);
    },
  });

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    // Send via REST (saves to DB) + WS broadcasts to other side
    sendMessage.mutate(input.trim());
    // Also send via WS for instant display on other side
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content: input.trim() }));
    }
    setInput("");
  };

  // Merge DB messages + WS messages, deduplicate
  const allMessages = [...messages, ...wsMessages];

  // Scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [allMessages.length]);

  const otherUser =
    exchange.requester?.id === user?.id ? exchange.owner : exchange.requester;

  return (
    <div className={styles.window}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.avatar}>
            {otherUser?.avatar_url ? (
              <img src={otherUser.avatar_url} alt="" />
            ) : (
              otherUser?.username?.[0]?.toUpperCase()
            )}
          </div>
          <div>
            <span className={styles.name}>{otherUser?.username}</span>
            <span className={styles.subtext}>
              📖 {exchange.requested_book?.title}
            </span>
          </div>
        </div>
        <button className={styles.closeBtn} onClick={onClose}>
          ✕
        </button>
      </div>

      <div className={styles.messages}>
        {allMessages.length === 0 && (
          <p className={styles.emptyMsg}>Почніть розмову про обмін 👋</p>
        )}
        {allMessages.map((msg, i) => {
          const isMine = (msg.sender?.id ?? msg.sender_id) === user?.id;
          return (
            <div
              key={msg.id ?? i}
              className={`${styles.bubble} ${isMine ? styles.mine : styles.theirs}`}
            >
              <p className={styles.bubbleText}>{msg.content}</p>
              <span className={styles.bubbleTime}>
                {new Date(msg.created_at).toLocaleTimeString("uk-UA", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <form className={styles.inputRow} onSubmit={handleSend}>
        <input
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Напишіть повідомлення..."
          autoFocus
        />
        <button
          type="submit"
          className={styles.sendBtn}
          disabled={!input.trim()}
        >
          ➤
        </button>
      </form>
    </div>
  );
}
