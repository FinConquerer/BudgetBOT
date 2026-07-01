/**
 * Khởi tạo i18next cho BudgetBOT. Ngôn ngữ lưu trong localStorage, mặc định tiếng Việt.
 * Không hardcode chuỗi UI — tất cả truy cập qua key t("domain.key").
 */
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import vi from "./locales/vi.json";
import en from "./locales/en.json";

const STORAGE_KEY = "bb-language";
const saved =
  typeof window !== "undefined" ? window.localStorage.getItem(STORAGE_KEY) : null;

i18n.use(initReactI18next).init({
  resources: { vi: { translation: vi }, en: { translation: en } },
  lng: saved === "en" || saved === "vi" ? saved : "vi",
  fallbackLng: "vi",
  interpolation: { escapeValue: false },
});

/** Đổi ngôn ngữ và lưu lựa chọn. @param {"vi"|"en"} lang */
export function setLanguage(lang) {
  i18n.changeLanguage(lang);
  if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, lang);
}

export default i18n;
