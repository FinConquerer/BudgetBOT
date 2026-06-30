/** API trợ lý hội thoại: hỏi nhanh (FAQ một lượt) và chat có lưu lịch sử (cần đăng nhập). */
import { apiFetch } from "./client.js";

/** Hỏi nhanh không cần đăng nhập. @param {string} question */
export function askFaq(question) {
  return apiFetch("/faq", { method: "POST", body: JSON.stringify({ question }) });
}

/** Tạo phiên chat mới. @param {string|null} title */
export function createChat(title = null) {
  return apiFetch("/chats", { method: "POST", body: JSON.stringify({ title }) });
}

export function listChats({ limit = 20, offset = 0 } = {}) {
  const q = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch(`/chats?${q.toString()}`);
}

/** Gửi câu hỏi trong một phiên chat. @param {string} chatId @param {string} message */
export function askInChat(chatId, message) {
  return apiFetch(`/chats/${chatId}/ask`, { method: "POST", body: JSON.stringify({ message }) });
}

export function listMessages(chatId, { limit = 50, offset = 0 } = {}) {
  const q = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch(`/chats/${chatId}/messages?${q.toString()}`);
}
