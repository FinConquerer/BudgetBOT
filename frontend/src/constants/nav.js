/** Dữ liệu điều hướng (data-driven). Nhãn là key i18n, dịch lúc render. */
import {
  HomeIcon,
  ChartPieIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  QuestionMarkCircleIcon,
} from "@heroicons/react/24/outline";

export const navSections = [
  {
    titleKey: "nav.section.main",
    items: [
      { labelKey: "nav.dashboard", path: "/", icon: HomeIcon },
      { labelKey: "nav.planner", path: "/planner", icon: ChartPieIcon },
      { labelKey: "nav.chat", path: "/chat", icon: ChatBubbleLeftRightIcon },
    ],
  },
  {
    titleKey: "nav.section.tools",
    items: [
      { labelKey: "nav.history", path: "/history", icon: ClockIcon },
      { labelKey: "nav.faq", path: "/faq", icon: QuestionMarkCircleIcon },
    ],
  },
];

/** Suy ra key tiêu đề trang từ pathname. @param {string} pathname */
export function titleKeyFromPath(pathname) {
  if (pathname.startsWith("/planner")) return "nav.planner";
  if (pathname.startsWith("/chat")) return "nav.chat";
  if (pathname.startsWith("/history")) return "nav.history";
  if (pathname.startsWith("/faq")) return "nav.faq";
  return "nav.dashboard";
}
