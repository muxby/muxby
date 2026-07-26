import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuditPage } from "./pages/AuditPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HospitalDetailPage } from "./pages/HospitalDetailPage";
import { HospitalsPage } from "./pages/HospitalsPage";
import { LoginPage } from "./pages/LoginPage";
import { ModelDetailPage } from "./pages/ModelDetailPage";
import { ModelsPage } from "./pages/ModelsPage";
import { NewRoundPage } from "./pages/NewRoundPage";
import { PredictionsHistoryPage } from "./pages/PredictionsHistoryPage";
import { PredictPage } from "./pages/PredictPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { RoundDetailPage } from "./pages/RoundDetailPage";
import { RoundsPage } from "./pages/RoundsPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/hospitals" element={<HospitalsPage />} />
        <Route path="/hospitals/:id" element={<HospitalDetailPage />} />
        <Route path="/rounds" element={<RoundsPage />} />
        <Route path="/rounds/new" element={<NewRoundPage />} />
        <Route path="/rounds/:id" element={<RoundDetailPage />} />
        <Route path="/models" element={<ModelsPage />} />
        <Route path="/models/:id" element={<ModelDetailPage />} />
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/predictions" element={<PredictionsHistoryPage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
