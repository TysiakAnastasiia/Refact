import { Book } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import useAuthStore from "../../store/authStore";
import styles from "./Layout.module.css";

export default function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className={styles.wrapper}>
      <nav className={styles.nav}>
        <div className={styles.navInner}>
          <NavLink to="/" className={styles.logo}>
            <Book className={styles.logoIcon} />
            <span className={styles.logoText}>BookSwap</span>
          </NavLink>

          <div className={styles.navLinks}>
            <NavLink
              to="/catalog"
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.active : ""}`
              }
            >
              Каталог
            </NavLink>
            <NavLink
              to="/exchange"
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.active : ""}`
              }
            >
              Обмін
            </NavLink>
            {user && (
              <>
                <NavLink
                  to="/wishlist"
                  className={({ isActive }) =>
                    `${styles.link} ${isActive ? styles.active : ""}`
                  }
                >
                  Бажання
                </NavLink>
                <NavLink
                  to="/recommendations"
                  className={({ isActive }) =>
                    `${styles.link} ${isActive ? styles.active : ""}`
                  }
                >
                  ✨ Для мене
                </NavLink>
              </>
            )}
          </div>

          <div className={styles.navRight}>
            {user ? (
              <>
                <NavLink to="/profile" className={styles.avatarLink}>
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.username}
                      className={styles.avatar}
                    />
                  ) : (
                    <div className={styles.avatarFallback}>
                      {user.username[0].toUpperCase()}
                    </div>
                  )}
                  <span className={styles.username}>{user.username}</span>
                </NavLink>
                <button onClick={handleLogout} className={styles.logoutBtn}>
                  Вийти
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={styles.loginBtn}>
                  Увійти
                </NavLink>
                <NavLink to="/register" className={styles.registerBtn}>
                  Реєстрація
                </NavLink>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className={styles.main}>
        <Outlet />
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <Book className={styles.footerLogo} />{" "}
          <span className={styles.logoText}>BookSwap</span>
          <span className={styles.footerText}>
            Діліться книгами — діліться знаннями
          </span>
        </div>
      </footer>
    </div>
  );
}
