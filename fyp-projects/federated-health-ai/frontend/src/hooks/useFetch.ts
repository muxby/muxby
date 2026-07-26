import { useCallback, useEffect, useRef, useState } from "react";

export interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
  /** Replace the cached data locally (e.g. after a mutation or socket event). */
  setData: (updater: (prev: T | null) => T | null) => void;
}

/**
 * Small data-loading hook: runs `fn` on mount and whenever `deps` change,
 * tracking loading/error state and ignoring out-of-order responses.
 */
export function useFetch<T>(
  fn: () => Promise<T>,
  deps: readonly unknown[],
): FetchState<T> {
  const [data, setDataState] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);
  const requestSeq = useRef(0);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    const seq = ++requestSeq.current;
    setLoading(true);
    setError(null);
    fnRef
      .current()
      .then((result) => {
        if (seq === requestSeq.current) {
          setDataState(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (seq === requestSeq.current) {
          setError(err instanceof Error ? err.message : "Request failed");
          setLoading(false);
        }
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, version]);

  const reload = useCallback(() => setVersion((v) => v + 1), []);
  const setData = useCallback(
    (updater: (prev: T | null) => T | null) => setDataState(updater),
    [],
  );

  return { data, loading, error, reload, setData };
}
