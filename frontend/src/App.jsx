/** Định tuyến ứng dụng. Pages tải lười (lazy) để chia nhỏ bundle (ECharts chỉ tải khi vào Planner). */
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import AppLayout from "./layout/AppLayout.jsx";

const Dashboard = lazy(() => import("./pages/Dashboard.jsx"));
const Planner = lazy(() => import("./pages/Planner.jsx"));
const Chat = lazy(() => import("./pages/Chat.jsx"));
const History = lazy(() => import("./pages/History.jsx"));
const Faq = lazy(() => import("./pages/Faq.jsx"));
const Login = lazy(() => import("./pages/Login.jsx"));
const Register = lazy(() => import("./pages/Register.jsx"));
const NotFound = lazy(() => import("./pages/NotFound.jsx"));

function Fallback() {
  return (
    <Box sx={{ height: "100vh", display: "grid", placeItems: "center" }}>
      <CircularProgress />
    </Box>
  );
}

export default function App() {
  return (
    <Suspense fallback={<Fallback />}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/history" element={<History />} />
          <Route path="/faq" element={<Faq />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
