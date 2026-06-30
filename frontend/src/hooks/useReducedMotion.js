/**
 * Hook reactive theo media query prefers-reduced-motion. Dùng cho component cần
 * phản ứng tức thời (vd Dialog). SSR-safe.
 */
import { useEffect, useState } from "react";

const QUERY = "(prefers-reduced-motion: reduce)";

export default function useReducedMotion() {
  const [reduced, setReduced] = useState(
    () => typeof window !== "undefined" && window.matchMedia?.(QUERY).matches,
  );

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return undefined;
    const mq = window.matchMedia(QUERY);
    const handler = (e) => setReduced(e.matches);
    mq.addEventListener?.("change", handler);
    return () => mq.removeEventListener?.("change", handler);
  }, []);

  return Boolean(reduced);
}
