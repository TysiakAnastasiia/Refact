// LoginPage.jsx
import { Book } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import styles from "./AuthPage.module.css";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const result = await login(email, password);
    if (result.success) navigate("/");
    else setError(result.error);
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>
          <Book className={styles.logoIcon} />
        </div>
        <h1 className={styles.title}>Вітаємо назад</h1>
        <p className={styles.sub}>Увійдіть до свого акаунту BookSwap</p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.field}>
            <label className={styles.label}>Email</label>
            <input
              className={styles.input}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              autoFocus
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Пароль</label>
            <input
              className={styles.input}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ваш пароль"
              required
            />
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" className={styles.submit} disabled={isLoading}>
            {isLoading ? "Вхід..." : "Увійти"}
          </button>
        </form>

        <p className={styles.footer}>
          Немає акаунту?{" "}
          <Link to="/register" className={styles.link}>
            Зареєструватись
          </Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;

// RegisterPage.jsx
export function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const { register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const set = (f) => (e) => setForm((p) => ({ ...p, [f]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const result = await register(
      form.email,
      form.username,
      form.password,
      form.full_name
    );
    if (result.success) navigate("/");
    else setError(result.error);
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>
          <Book className={styles.logoIcon} />
        </div>
        <h1 className={styles.title}>Приєднатися до BookSwap</h1>
        <p className={styles.sub}>Створіть безкоштовний акаунт</p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.field}>
            <label className={styles.label}>Ім'я та прізвище</label>
            <input
              className={styles.input}
              value={form.full_name}
              onChange={set("full_name")}
              placeholder="Іван Франко"
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Нікнейм *</label>
            <input
              className={styles.input}
              value={form.username}
              onChange={set("username")}
              placeholder="bookworm"
              required
              minLength={3}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Email *</label>
            <input
              className={styles.input}
              type="email"
              value={form.email}
              onChange={set("email")}
              placeholder="your@email.com"
              required
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Пароль *</label>
            <input
              className={styles.input}
              type="password"
              value={form.password}
              onChange={set("password")}
              placeholder="Мінімум 8 символів"
              required
              minLength={8}
            />
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" className={styles.submit} disabled={isLoading}>
            {isLoading ? "Реєстрація..." : "Зареєструватись"}
          </button>
        </form>

        <p className={styles.footer}>
          Вже є акаунт?{" "}
          <Link to="/login" className={styles.link}>
            Увійти
          </Link>
        </p>
      </div>
    </div>
  );
}
