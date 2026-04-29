import { MessageCircle, Send, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { chatApi } from "../../api/client";
import useAuthStore from "../../store/authStore";
import styles from "./ChatModal.module.css";

export default function ChatModal({ exchange, onClose }) {
  const { user: currentUser } = useAuthStore();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const messagesEndRef = useRef(null);

  const loadMessages = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await chatApi.getMessages(exchange.id);
      setMessages(response.data);
    } catch (error) {
      console.error("Error loading messages:", error);
    } finally {
      setIsLoading(false);
    }
  }, [exchange]);

  useEffect(() => {
    if (exchange) {
      loadMessages();
    }
  }, [exchange, loadMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

    try {
      setIsLoading(true);
      const response = await chatApi.getMessages(exchange.id);
      setMessages(response.data);
    } catch (error) {
      console.error("Error loading messages:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !exchange) return;

    try {
      const response = await chatApi.send(exchange.id, newMessage);
      setMessages((prev) => [...prev, response.data]);
      setNewMessage("");
      scrollToBottom();
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  if (!exchange) return null;

  const otherUser =
    exchange.requester?.id === currentUser?.id
      ? exchange.owner
      : exchange.requester;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div className={styles.chatInfo}>
            <div className={styles.avatar}>
              {otherUser?.avatar_url ? (
                <img src={otherUser.avatar_url} alt={otherUser.username} />
              ) : (
                <div className={styles.avatarPlaceholder}>
                  {otherUser?.username?.charAt(0)?.toUpperCase()}
                </div>
              )}
            </div>
            <div>
              <h3>{otherUser?.full_name || otherUser?.username}</h3>
              <p className={styles.exchangeInfo}>
                Обмін книгами #{exchange.id}
              </p>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className={styles.chatContainer}>
          {isLoading ? (
            <div className={styles.loading}>
              <MessageCircle className={styles.loadingIcon} size={24} />
              <p>Завантаження повідомлень...</p>
            </div>
          ) : (
            <div className={styles.messagesList}>
              {messages.length === 0 ? (
                <div className={styles.emptyChat}>
                  <MessageCircle size={48} />
                  <p>Ще немає повідомлень</p>
                  <p>Почніть розмову першим!</p>
                </div>
              ) : (
                messages.map((message) => {
                  const isOwn = message.sender_id === currentUser?.id;
                  const senderName = isOwn
                    ? currentUser?.full_name || currentUser?.username
                    : message.sender?.full_name ||
                      message.sender?.username ||
                      otherUser?.full_name ||
                      otherUser?.username;

                  return (
                    <div
                      key={message.id}
                      className={`${styles.message} ${
                        isOwn ? styles.ownMessage : styles.otherMessage
                      }`}
                    >
                      <div className={styles.messageContent}>
                        {!isOwn && (
                          <span className={styles.senderName}>
                            {senderName}
                          </span>
                        )}
                        <p>{message.content}</p>
                        <span className={styles.messageTime}>
                          {new Date(message.created_at).toLocaleTimeString(
                            "uk-UA",
                            {
                              hour: "2-digit",
                              minute: "2-digit",
                            }
                          )}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <form className={styles.messageForm} onSubmit={handleSendMessage}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Напишіть повідомлення..."
            className={styles.messageInput}
          />
          <button
            type="submit"
            disabled={!newMessage.trim()}
            className={styles.sendBtn}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
