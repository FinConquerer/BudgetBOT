/** API danh mục FAQ công khai (không cần đăng nhập). */
import { apiFetch } from "./client.js";

/** @param {{q?:string, limit?:number, offset?:number}} [params] */
export function listFaqs({ q, limit = 20, offset = 0 } = {}) {
  const sp = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (q) sp.set("q", q);
  return apiFetch(`/faqs?${sp.toString()}`);
}
