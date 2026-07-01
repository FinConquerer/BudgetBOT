/**
 * Đăng ký GSAP một chỗ + hook animation. Mọi animation phải tôn trọng reduced-motion:
 * guard bằng `if (reduced(theme)) return;`.
 */
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);

/** Cờ reduced-motion đọc từ theme (đặt lúc dựng theme). @param {object} theme */
export function reduced(theme) {
  return Boolean(theme?.motion?.reducedMotion);
}

/**
 * Fade + trượt nhẹ các phần tử khớp selector khi mount (stagger).
 * @param {React.RefObject} scopeRef - ref bọc vùng cần animate
 * @param {object} theme
 * @param {{selector?: string}} [opts]
 */
export function useStaggerIn(scopeRef, theme, { selector = ".gsap-in" } = {}) {
  useGSAP(
    () => {
      if (reduced(theme)) return;
      const els = scopeRef.current?.querySelectorAll(selector);
      if (!els || !els.length) return;
      gsap.from(els, { opacity: 0, y: 10, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    },
    { scope: scopeRef, dependencies: [] },
  );
}

export { gsap, useGSAP, useRef };
