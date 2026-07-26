import { useEffect, useRef, useState } from "react";
import { roundSocketUrl } from "../api/client";
import type { RoundSocketEvent } from "../api/types";
import { useAuthStore } from "../stores/authStore";

const MAX_RECONNECTS = 4;
const RECONNECT_DELAY_MS = 2500;

/**
 * Subscribes to the live training-round WebSocket feed.
 * Calls `onEvent` for every parsed server event. Attempts a few reconnects,
 * then reports `connected: false` so callers can fall back to polling.
 */
export function useRoundSocket(
  roundId: number | null,
  enabled: boolean,
  onEvent: (event: RoundSocketEvent) => void,
): { connected: boolean } {
  const [connected, setConnected] = useState(false);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    if (roundId === null || !enabled || !token) {
      setConnected(false);
      return;
    }

    let socket: WebSocket | null = null;
    let attempts = 0;
    let closedByCleanup = false;
    let reconnectTimer: number | undefined;

    const connect = () => {
      socket = new WebSocket(roundSocketUrl(roundId, token));
      socket.onopen = () => {
        attempts = 0;
        setConnected(true);
      };
      socket.onmessage = (msg: MessageEvent<string>) => {
        try {
          const event = JSON.parse(msg.data) as RoundSocketEvent;
          if (event && typeof event.type === "string") {
            onEventRef.current(event);
          }
        } catch {
          // ignore malformed frames
        }
      };
      socket.onclose = () => {
        setConnected(false);
        if (!closedByCleanup && attempts < MAX_RECONNECTS) {
          attempts += 1;
          reconnectTimer = window.setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };
      socket.onerror = () => {
        socket?.close();
      };
    };

    connect();

    return () => {
      closedByCleanup = true;
      window.clearTimeout(reconnectTimer);
      socket?.close();
      setConnected(false);
    };
  }, [roundId, enabled, token]);

  return { connected };
}
