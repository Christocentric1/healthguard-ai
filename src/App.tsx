import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { logApiConfig } from "@/lib/api";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import AlertDetail from "./pages/AlertDetail";
import Endpoints from "./pages/Endpoints";
import Compliance from "./pages/Compliance";
import MITREAttack from "./pages/MITREAttack";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Log API configuration on app startup
logApiConfig();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/alerts/:id" element={<AlertDetail />} />
              <Route path="/endpoints" element={<Endpoints />} />
              <Route path="/compliance" element={<Compliance />} />
              <Route path="/mitre-attack" element={<MITREAttack />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
