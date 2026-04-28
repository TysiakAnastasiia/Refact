import { useQuery } from "@tanstack/react-query";
import { Check, MessageCircle, Search, UserPlus } from "lucide-react";
import { useState } from "react";
import { exchangesApi, friendsApi, usersApi } from "../api/client";
import ChatModal from "../components/modals/ChatModal";
import UserProfileModal from "../components/modals/UserProfileModal";
import StarRating from "../components/ui/StarRating";
import useAuthStore from "../store/authStore";
import styles from "./UsersPage.module.css";

export default function UsersPage() {
  const { user: currentUser } = useAuthStore();
  const [activeTab, setActiveTab] = useState("search");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [buttonFeedback, setButtonFeedback] = useState({});
  const [selectedUser, setSelectedUser] = useState(null);
  const [chatExchange, setChatExchange] = useState(null);

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["users", "search", searchQuery],
    queryFn: () => usersApi.search(searchQuery).then((r) => r.data),
    enabled: searchQuery.length > 0,
  });

  const { data: friends = [] } = useQuery({
    queryKey: ["friends"],
    queryFn: () => friendsApi.get().then((r) => r.data),
    enabled: !!currentUser,
  });

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchQuery(searchTerm);
  };

  const handleAddFriend = async (userId) => {
    if (!currentUser) return;

    try {
      await friendsApi.add(userId);
      setButtonFeedback((prev) => ({
        ...prev,
        [userId]: {
          type: "friend",
          status: "success",
          message: "Додано в друзі",
        },
      }));
      console.log("Friend added successfully:", userId);
    } catch (error) {
      console.error("Error adding friend:", error);
      setButtonFeedback((prev) => ({
        ...prev,
        [userId]: { type: "friend", status: "error", message: "Помилка" },
      }));
    }

    setTimeout(() => {
      setButtonFeedback((prev) => ({ ...prev, [userId]: null }));
    }, 2000);
  };

  const handleMessage = async (userId) => {
    if (!currentUser) return;

    try {
      // Check if there's already an exchange between users
      const existingExchanges = await exchangesApi.getBetweenUsers(
        currentUser.id,
        userId
      );

      if (existingExchanges.data.length > 0) {
        // Found existing exchange, open chat modal
        const exchange = existingExchanges.data[0];
        setButtonFeedback((prev) => ({
          ...prev,
          [userId]: {
            type: "message",
            status: "success",
            message: "Чат відкрито",
          },
        }));
        console.log("Opening chat modal for exchange:", exchange.id);
        // Open chat modal
        setTimeout(() => {
          setChatExchange(exchange);
        }, 500);
      } else {
        // No existing exchange, show message
        setButtonFeedback((prev) => ({
          ...prev,
          [userId]: {
            type: "message",
            status: "error",
            message: "Спочатку створіть обмін",
          },
        }));
        console.log("No exchange found with user:", userId);
      }

      // Clear feedback after 2 seconds
      setTimeout(() => {
        setButtonFeedback((prev) => ({ ...prev, [userId]: null }));
      }, 2000);
    } catch (error) {
      console.error("Error handling message:", error);
      setButtonFeedback((prev) => ({
        ...prev,
        [userId]: { type: "message", status: "error", message: "Помилка" },
      }));
      setTimeout(() => {
        setButtonFeedback((prev) => ({ ...prev, [userId]: null }));
      }, 2000);
    }
  };

  const handleViewProfile = (user) => {
    setSelectedUser(user);
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>Користувачі</h1>
        <p className={styles.subtitle}>
          Знайдіть нових друзів та спілкуйтесь з ними
        </p>

        {/* Tabs */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === "search" ? styles.activeTab : ""}`}
            onClick={() => setActiveTab("search")}
          >
            <Search size={16} />
            Пошук
          </button>
          <button
            className={`${styles.tab} ${activeTab === "friends" ? styles.activeTab : ""}`}
            onClick={() => setActiveTab("friends")}
          >
            <UserPlus size={16} />
            Друзі
          </button>
        </div>

        {/* Search Tab Content */}
        {activeTab === "search" && (
          <div>
            <form className={styles.searchForm} onSubmit={handleSearch}>
              <div className={styles.searchInputWrapper}>
                <Search className={styles.searchIcon} />
                <input
                  type="text"
                  placeholder="Пошук за іменем, ніком або email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className={styles.searchInput}
                />
              </div>
              <button
                type="submit"
                className={styles.searchBtn}
                disabled={isLoading}
              >
                {isLoading ? "Пошук..." : "Знайти"}
              </button>
            </form>

            {/* Results */}
            {searchQuery && (
              <div className={styles.results}>
                <h2 className={styles.resultsTitle}>
                  {users.length > 0
                    ? `Знайдено користувачів: ${users.length}`
                    : "Користувачів не знайдено"}
                </h2>

                {users.length === 0 && searchQuery && !isLoading && (
                  <div className={styles.empty}>
                    <p>Спробуйте змінити пошуковий запит</p>
                  </div>
                )}

                <div className={styles.usersGrid}>
                  {users.map((user) => (
                    <div key={user.id} className={styles.userCard}>
                      <div className={styles.userHeader}>
                        <div className={styles.avatar}>
                          {user.avatar_url ? (
                            <img src={user.avatar_url} alt="" />
                          ) : (
                            <UserPlus className={styles.avatarIcon} />
                          )}
                        </div>
                        <div className={styles.userInfo}>
                          <h3
                            className={styles.userName}
                            onClick={() => handleViewProfile(user)}
                            style={{
                              cursor: "pointer",
                              textDecoration: "underline",
                            }}
                          >
                            {user.full_name || user.username}
                          </h3>
                          <p className={styles.userHandle}>@{user.username}</p>
                          {user.city && (
                            <p className={styles.userCity}>📍 {user.city}</p>
                          )}
                        </div>
                      </div>

                      {user.bio && <p className={styles.userBio}>{user.bio}</p>}

                      <div className={styles.userStats}>
                        <div className={styles.stat}>
                          <span className={styles.statNum}>
                            {user.review_count || 0}
                          </span>
                          <span className={styles.statLabel}>Рецензій</span>
                        </div>
                        <div className={styles.stat}>
                          <span className={styles.statNum}>
                            {user.book_count || 0}
                          </span>
                          <span className={styles.statLabel}>Книг</span>
                        </div>
                        <div className={styles.stat}>
                          <span className={styles.statNum}>
                            {user.rating || "—"}
                          </span>
                          <span className={styles.statLabel}>Оцінка</span>
                        </div>
                      </div>

                      {user.rating && (
                        <div className={styles.rating}>
                          <StarRating rating={user.rating} size="sm" />
                          <span className={styles.ratingText}>
                            {user.rating}
                          </span>
                        </div>
                      )}

                      <div className={styles.userActions}>
                        <button
                          className={`${styles.actionBtn} ${buttonFeedback[user.id]?.type === "friend" && buttonFeedback[user.id]?.status === "success" ? styles.successBtn : ""}`}
                          onClick={() => handleAddFriend(user.id)}
                          disabled={user.id === currentUser?.id}
                        >
                          {buttonFeedback[user.id]?.type === "friend" &&
                          buttonFeedback[user.id]?.status === "success" ? (
                            <Check size={16} />
                          ) : (
                            <UserPlus size={16} />
                          )}
                          {buttonFeedback[user.id]?.type === "friend" &&
                          buttonFeedback[user.id]?.status === "success"
                            ? "Запит надіслано"
                            : "Додати в друзі"}
                        </button>
                        <button
                          className={`${styles.actionBtn} ${
                            buttonFeedback[user.id]?.type === "message" &&
                            buttonFeedback[user.id]?.status === "success"
                              ? styles.successBtn
                              : buttonFeedback[user.id]?.type === "message" &&
                                  buttonFeedback[user.id]?.status === "error"
                                ? styles.errorBtn
                                : ""
                          }`}
                          onClick={() => handleMessage(user.id)}
                          disabled={user.id === currentUser?.id}
                        >
                          {buttonFeedback[user.id]?.type === "message" &&
                          buttonFeedback[user.id]?.status === "success" ? (
                            <Check size={16} />
                          ) : buttonFeedback[user.id]?.type === "message" &&
                            buttonFeedback[user.id]?.status === "error" ? (
                            <MessageCircle size={16} />
                          ) : (
                            <MessageCircle size={16} />
                          )}
                          {buttonFeedback[user.id]?.type === "message" &&
                          buttonFeedback[user.id]?.status === "success"
                            ? buttonFeedback[user.id]?.message || "Відкрито чат"
                            : buttonFeedback[user.id]?.type === "message" &&
                                buttonFeedback[user.id]?.status === "error"
                              ? buttonFeedback[user.id]?.message || "Помилка"
                              : "Повідомлення"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!searchQuery && (
              <div className={styles.empty}>
                <Search className={styles.emptyIcon} />
                <h3>Введіть пошуковий запит</h3>
                <p>Спробуйте шукати за іменем, ніком або email користувача</p>
              </div>
            )}
          </div>
        )}

        {/* Friends Tab Content */}
        {activeTab === "friends" && (
          <div className={styles.friendsSection}>
            {friends.length === 0 ? (
              <div className={styles.empty}>
                <UserPlus className={styles.emptyIcon} />
                <h3>У вас ще немає друзів</h3>
                <p>Знайдіть користувачів через пошук та додайте їх в друзі</p>
              </div>
            ) : (
              <div>
                <h2 className={styles.resultsTitle}>
                  Ваші друзі: {friends.length}
                </h2>
                <div className={styles.usersGrid}>
                  {friends.map((friend) => (
                    <div key={friend.id} className={styles.userCard}>
                      <div className={styles.userHeader}>
                        <div className={styles.avatar}>
                          {friend.avatar_url ? (
                            <img src={friend.avatar_url} alt="" />
                          ) : (
                            <UserPlus className={styles.avatarIcon} />
                          )}
                        </div>
                        <div className={styles.userInfo}>
                          <h3
                            className={styles.userName}
                            onClick={() => handleViewProfile(friend)}
                            style={{
                              cursor: "pointer",
                              textDecoration: "underline",
                            }}
                          >
                            {friend.full_name || friend.username}
                          </h3>
                          <p className={styles.userHandle}>
                            @{friend.username}
                          </p>
                          {friend.city && (
                            <p className={styles.userCity}>📍 {friend.city}</p>
                          )}
                        </div>
                      </div>

                      {friend.bio && (
                        <p className={styles.userBio}>{friend.bio}</p>
                      )}

                      <div className={styles.userStats}>
                        <div className={styles.stat}>
                          <span className={styles.statNum}>
                            {friend.review_count || 0}
                          </span>
                          <span className={styles.statLabel}>Рецензій</span>
                        </div>
                        <div className={styles.stat}>
                          <span className={styles.statNum}>
                            {friend.book_count || 0}
                          </span>
                          <span className={styles.statLabel}>Книг</span>
                        </div>
                        <div className={styles.stat}>
                          <span className={styles.statNum}>
                            {friend.rating || "—"}
                          </span>
                          <span className={styles.statLabel}>Оцінка</span>
                        </div>
                      </div>

                      <div className={styles.userActions}>
                        <button
                          className={styles.actionBtn}
                          onClick={() => handleMessage(friend.id)}
                        >
                          <MessageCircle size={16} />
                          Повідомлення
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* User Profile Modal */}
      {selectedUser && (
        <UserProfileModal
          user={selectedUser}
          onClose={() => setSelectedUser(null)}
        />
      )}

      {/* Chat Modal */}
      {chatExchange && (
        <ChatModal
          exchange={chatExchange}
          onClose={() => setChatExchange(null)}
        />
      )}
    </div>
  );
}
