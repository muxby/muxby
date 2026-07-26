import { create } from "zustand";
import type { User } from "../api/types";

const TOKEN_KEY = "fedhealth.token";

function readStoredToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: readStoredToken(),
  user: null,
  setToken: (token) => {
    try {
      window.localStorage.setItem(TOKEN_KEY, token);
    } catch {
      // storage unavailable; keep the token in memory only
    }
    set({ token });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    try {
      window.localStorage.removeItem(TOKEN_KEY);
    } catch {
      // storage unavailable; nothing to clear
    }
    set({ token: null, user: null });
  },
}));
