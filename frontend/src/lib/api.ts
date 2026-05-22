import type { OrderDetail, OrderSummary, User, UserCreate } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getMe: () => request<User>("/auth/me"),

  changePassword: (current_password: string, new_password: string) =>
    request<{ message: string }>("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password, new_password }),
    }),

  getOrders: () => request<OrderSummary[]>("/orders"),

  getOrder: (orderNbr: string) =>
    request<OrderDetail>(`/orders/${encodeURIComponent(orderNbr)}`),

  // Admin
  getUsers: () => request<User[]>("/admin/users"),

  createUser: (data: UserCreate) =>
    request<User>("/admin/users", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateUser: (id: number, data: Partial<User>) =>
    request<User>(`/admin/users/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteUser: (id: number) =>
    request<void>(`/admin/users/${id}`, { method: "DELETE" }),

  markInspected: (sales_order_nbr: string, line_nbr: number, notes?: string) =>
    request<{ message: string }>("/admin/inspect", {
      method: "POST",
      body: JSON.stringify({ sales_order_nbr, line_nbr, notes }),
    }),

  unmarkInspected: (sales_order_nbr: string, line_nbr: number) =>
    request<void>(`/admin/inspect/${encodeURIComponent(sales_order_nbr)}/${line_nbr}`, {
      method: "DELETE",
    }),
};

export { ApiError };
