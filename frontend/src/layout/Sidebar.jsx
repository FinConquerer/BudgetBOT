/** Sidebar điều hướng: Drawer permanent (desktop) + temporary (mobile), cùng dùng SidebarContent. */
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { NavLink, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { navSections } from "../constants/nav.js";

export const DRAWER_WIDTH = 256;

function isActive(path, pathname) {
  return path === "/" ? pathname === "/" : pathname.startsWith(path);
}

function SidebarContent({ onNavigate }) {
  const { t } = useTranslation();
  const { pathname } = useLocation();

  return (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Toolbar sx={{ minHeight: 70 }}>
        <Stack direction="row" spacing={1.25} alignItems="center">
          <Box sx={{ fontSize: 24 }}>💰</Box>
          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            BudgetBOT
          </Typography>
        </Stack>
      </Toolbar>

      <Box sx={{ px: 2, py: 1, overflowY: "auto" }}>
        {navSections.map((section) => (
          <Box key={section.titleKey} sx={{ mb: 2 }}>
            <Typography
              variant="overline"
              color="text.secondary"
              sx={{ px: 1.5, fontWeight: 700 }}
            >
              {t(section.titleKey)}
            </Typography>
            <List disablePadding>
              {section.items.map((item) => {
                const active = isActive(item.path, pathname);
                const Icon = item.icon;
                return (
                  <ListItemButton
                    key={item.path}
                    component={NavLink}
                    to={item.path}
                    onClick={onNavigate}
                    sx={{
                      borderRadius: 2,
                      mb: 0.5,
                      color: active ? "primary.main" : "text.primary",
                      bgcolor: active ? "rgba(99,102,241,0.12)" : "transparent",
                      "&:hover": { bgcolor: active ? "rgba(99,102,241,0.18)" : "action.hover" },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40, color: "inherit" }}>
                      <Icon style={{ width: 22, height: 22 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={t(item.labelKey)}
                      primaryTypographyProps={{ fontWeight: active ? 700 : 500 }}
                    />
                  </ListItemButton>
                );
              })}
            </List>
          </Box>
        ))}
      </Box>
    </Box>
  );
}

/** @param {{mobileOpen:boolean, onClose:()=>void}} props */
export default function Sidebar({ mobileOpen, onClose }) {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));

  if (isDesktop) {
    return (
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
            borderRight: "1px solid",
            borderColor: "divider",
          },
        }}
        open
      >
        <SidebarContent />
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="temporary"
      open={mobileOpen}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      sx={{ "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box" } }}
    >
      <SidebarContent onNavigate={onClose} />
    </Drawer>
  );
}
