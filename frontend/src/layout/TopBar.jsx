/** Thanh trên: mở sidebar (mobile), tiêu đề trang, đổi ngôn ngữ, đổi sáng/tối, tài khoản. */
import { useState } from "react";
import {
  AppBar,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
  Divider,
} from "@mui/material";
import {
  Bars3Icon,
  SunIcon,
  MoonIcon,
  LanguageIcon,
  UserCircleIcon,
} from "@heroicons/react/24/outline";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { DRAWER_WIDTH } from "./Sidebar.jsx";
import { useColorMode } from "../theme/ColorModeContext.jsx";
import { useAuth } from "../auth/AuthContext.jsx";
import { setLanguage } from "../i18n/index.js";
import { titleKeyFromPath } from "../constants/nav.js";

/** @param {{onMenuClick:()=>void}} props */
export default function TopBar({ onMenuClick }) {
  const { t, i18n } = useTranslation();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { mode, toggle } = useColorMode();
  const { isAuthed, user, logout } = useAuth();
  const [anchor, setAnchor] = useState(null);

  const nextLang = i18n.language === "vi" ? "en" : "vi";

  return (
    <AppBar
      position="fixed"
      color="default"
      elevation={0}
      sx={{
        width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
        ml: { md: `${DRAWER_WIDTH}px` },
        bgcolor: "background.paper",
        borderBottom: "1px solid",
        borderColor: "divider",
      }}
    >
      <Toolbar sx={{ minHeight: 70, gap: 1 }}>
        <IconButton edge="start" onClick={onMenuClick} sx={{ display: { md: "none" } }}>
          <Bars3Icon style={{ width: 24, height: 24 }} />
        </IconButton>

        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
          {t(titleKeyFromPath(pathname))}
        </Typography>

        <Tooltip title={t("topbar.language")}>
          <Button
            onClick={() => setLanguage(nextLang)}
            startIcon={<LanguageIcon style={{ width: 20, height: 20 }} />}
            color="inherit"
            size="small"
            className="no-hover-lift"
          >
            {i18n.language.toUpperCase()}
          </Button>
        </Tooltip>

        <Tooltip title={t("topbar.toggleTheme")}>
          <IconButton onClick={toggle} color="inherit">
            {mode === "dark" ? (
              <SunIcon style={{ width: 22, height: 22 }} />
            ) : (
              <MoonIcon style={{ width: 22, height: 22 }} />
            )}
          </IconButton>
        </Tooltip>

        {isAuthed ? (
          <>
            <Tooltip title={t("topbar.account")}>
              <IconButton onClick={(e) => setAnchor(e.currentTarget)} color="inherit">
                <UserCircleIcon style={{ width: 26, height: 26 }} />
              </IconButton>
            </Tooltip>
            <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={() => setAnchor(null)}>
              <Box sx={{ px: 2, py: 1 }}>
                <Typography variant="subtitle2">{user?.username}</Typography>
                {user?.email && (
                  <Typography variant="caption" color="text.secondary">
                    {user.email}
                  </Typography>
                )}
              </Box>
              <Divider />
              <MenuItem
                onClick={() => {
                  setAnchor(null);
                  logout();
                }}
              >
                {t("topbar.logout")}
              </MenuItem>
            </Menu>
          </>
        ) : (
          <Button variant="contained" size="small" onClick={() => navigate("/login")}>
            {t("topbar.login")}
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
