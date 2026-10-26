import { useEffect, useState, useCallback, useRef } from "react";
import { api } from "../services/api";
export function useData(path) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const activeRequest = useRef(null);
  const reload = useCallback(async () => {
    activeRequest.current?.abort();
    const controller = new AbortController();
    activeRequest.current = controller;
    setLoading(true);
    setError("");
    try {
      const result = await api(path, { signal: controller.signal });
      if (!controller.signal.aborted) setData(result);
    } catch (error) {
      if (!controller.signal.aborted) setError(error.message);
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }, [path]);
  useEffect(() => {
    reload();
    return () => activeRequest.current?.abort();
  }, [reload]);
  return { data, error, loading, reload };
}
