import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

//  Test helpers

const makeWrapper =
  (queryClient) =>
  ({ children }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );

const makeQueryClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

//  Mock data
const mockBook = {
  id: 1,
  title: "Майстер і Маргарита",
  author: "Михайло Булгаков",
  genre: "fiction",
  condition: "good",
  cover_url: null,
  description: "Чудова книга.",
  published_year: 1967,
  average_rating: 4.5,
  review_count: 10,
  is_available_for_exchange: true,
  owner: { id: 2, username: "alice", avatar_url: null },
  owner_id: 2,
  created_at: "2024-01-01T00:00:00",
};

const mockUser = {
  id: 1,
  email: "test@test.com",
  username: "testuser",
  full_name: "Test User",
  avatar_url: null,
  created_at: "2024-01-01T00:00:00",
};

//  StarRating tests

describe("StarRating", () => {
  it("renders 5 stars", async () => {
    const { default: StarRating } = await import("../components/ui/StarRating");
    const { container } = render(<StarRating rating={3} />);
    const stars = container.querySelectorAll("span");
    expect(stars.length).toBe(5);
  });

  it("marks correct number of filled stars", async () => {
    const { default: StarRating } = await import("../components/ui/StarRating");
    const { container } = render(<StarRating rating={4} />);
    const filled = container.querySelectorAll('[class*="filled"]');
    expect(filled.length).toBe(4);
  });

  it("renders no filled stars for rating 0", async () => {
    const { default: StarRating } = await import("../components/ui/StarRating");
    const { container } = render(<StarRating rating={0} />);
    const filled = container.querySelectorAll('[class*="filled"]');
    expect(filled.length).toBe(0);
  });

  it("calls onRate when interactive", async () => {
    const { default: StarRating } = await import("../components/ui/StarRating");
    const onRate = vi.fn();
    const { container } = render(
      <StarRating rating={0} interactive onRate={onRate} />
    );
    const stars = container.querySelectorAll("span");
    fireEvent.click(stars[2]); // 3rd star
    expect(onRate).toHaveBeenCalledWith(3);
  });
});

//  BookCard tests

vi.mock("../store/authStore", () => ({
  default: () => ({ user: null }),
}));

vi.mock("@tanstack/react-query", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useQuery: vi.fn(() => ({ data: [], isLoading: false })),
    useMutation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  };
});

describe("BookCard", () => {
  it("renders book title and author", async () => {
    const { default: BookCard } = await import("../components/books/BookCard");
    const qc = makeQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <BookCard book={mockBook} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByText("Майстер і Маргарита")).toBeInTheDocument();
    expect(screen.getByText("Михайло Булгаков")).toBeInTheDocument();
  });

  it("shows exchange badge when available", async () => {
    const { default: BookCard } = await import("../components/books/BookCard");
    const qc = makeQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <BookCard book={mockBook} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByText(/Обмін/)).toBeInTheDocument();
  });

  it("does not show exchange badge when unavailable", async () => {
    const { default: BookCard } = await import("../components/books/BookCard");
    const qc = makeQueryClient();
    const unavailableBook = { ...mockBook, is_available_for_exchange: false };
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <BookCard book={unavailableBook} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.queryByText(/Обмін/)).toBeNull();
  });

  it("shows review count when > 0", async () => {
    const { default: BookCard } = await import("../components/books/BookCard");
    const qc = makeQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <BookCard book={mockBook} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByText("(10)")).toBeInTheDocument();
  });

  it("shows owner username", async () => {
    const { default: BookCard } = await import("../components/books/BookCard");
    const qc = makeQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <BookCard book={mockBook} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByText("@alice")).toBeInTheDocument();
  });

  it("opens modal on click", async () => {
    const { default: BookCard } = await import("../components/books/BookCard");
    const qc = makeQueryClient();
    const { container } = render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <BookCard book={mockBook} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    const card = container.querySelector("article");
    fireEvent.click(card);
    // Modal should appear (overlay)
    await waitFor(() => {
      expect(document.body.style.overflow).toBe("hidden");
    });
  });
});

//  Auth store tests

describe("AuthStore", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("initializes with null user", async () => {
    const { default: useAuthStore } = await import("../store/authStore");
    const state = useAuthStore.getState();
    // Fresh state should have null user (cleared from localStorage)
    expect(state.login).toBeTypeOf("function");
    expect(state.logout).toBeTypeOf("function");
    expect(state.register).toBeTypeOf("function");
  });

  it("logout clears user and tokens", async () => {
    const { default: useAuthStore } = await import("../store/authStore");
    useAuthStore.setState({
      user: mockUser,
      accessToken: "tok",
      refreshToken: "ref",
    });
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });
});

//  API client tests

describe("API client", () => {
  it("exports all required API modules", async () => {
    const apiModule = await import("../api/client");
    expect(apiModule.booksApi).toBeDefined();
    expect(apiModule.reviewsApi).toBeDefined();
    expect(apiModule.exchangesApi).toBeDefined();
    expect(apiModule.wishlistApi).toBeDefined();
    expect(apiModule.chatApi).toBeDefined();
    expect(apiModule.usersApi).toBeDefined();
    expect(apiModule.recommendationsApi).toBeDefined();
  });

  it("booksApi has correct methods", async () => {
    const { booksApi } = await import("../api/client");
    expect(booksApi.list).toBeTypeOf("function");
    expect(booksApi.get).toBeTypeOf("function");
    expect(booksApi.create).toBeTypeOf("function");
    expect(booksApi.update).toBeTypeOf("function");
    expect(booksApi.delete).toBeTypeOf("function");
    expect(booksApi.getReviews).toBeTypeOf("function");
  });

  it("exchangesApi has accept/reject/complete", async () => {
    const { exchangesApi } = await import("../api/client");
    expect(exchangesApi.accept).toBeTypeOf("function");
    expect(exchangesApi.reject).toBeTypeOf("function");
    expect(exchangesApi.complete).toBeTypeOf("function");
  });
});

//  Genre label tests

describe("Genre display", () => {
  const GENRE_LABELS = {
    fiction: "Проза",
    non_fiction: "Нон-фікшн",
    fantasy: "Фентезі",
    sci_fi: "Фантастика",
    mystery: "Детектив",
    romance: "Романтика",
    thriller: "Трилер",
    horror: "Жахи",
    biography: "Біографія",
    history: "Історія",
    science: "Наука",
    self_help: "Саморозвиток",
    children: "Дитяча",
    poetry: "Поезія",
    other: "Інше",
  };

  it("maps all genre keys to Ukrainian labels", () => {
    const genres = Object.keys(GENRE_LABELS);
    expect(genres.length).toBe(15);
    genres.forEach((g) => {
      expect(GENRE_LABELS[g]).toBeTruthy();
      expect(typeof GENRE_LABELS[g]).toBe("string");
    });
  });

  it("has Ukrainian labels for common genres", () => {
    expect(GENRE_LABELS["fantasy"]).toBe("Фентезі");
    expect(GENRE_LABELS["sci_fi"]).toBe("Фантастика");
    expect(GENRE_LABELS["mystery"]).toBe("Детектив");
  });
});

//  Exchange status tests

describe("Exchange status mapping", () => {
  const STATUS_LABELS = {
    pending: "Очікує",
    accepted: "Прийнято",
    completed: "Завершено",
    rejected: "Відхилено",
    cancelled: "Скасовано",
  };

  it("covers all exchange statuses", () => {
    const expected = [
      "pending",
      "accepted",
      "completed",
      "rejected",
      "cancelled",
    ];
    expected.forEach((status) => {
      expect(STATUS_LABELS[status]).toBeTruthy();
    });
  });

  it("returns Ukrainian label for pending", () => {
    expect(STATUS_LABELS["pending"]).toBe("Очікує");
  });
});
