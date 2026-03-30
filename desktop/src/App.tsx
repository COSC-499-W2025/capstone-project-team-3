import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { pageList } from "./pages";
import WelcomePage from "./pages/WelcomePage";
import { getHealth } from "./api/health";
import { getConsentStatus } from "./api/consent";
import { useState, useEffect } from "react";
import { NavBar } from "./NavBar";
import { ThemeProvider } from "./context/ThemeContext";

function AppLayout() {
  const location = useLocation();
  const [hasConsent, setHasConsent] = useState<boolean | null>(null);

  useEffect(() => {
    getConsentStatus()
      .then(({ has_consent }) => setHasConsent(has_consent))
      .catch(() => setHasConsent(false));
  }, [location.pathname]);

  const showNavBar = hasConsent === true;

  return (
    <div className="app-layout">
      {showNavBar && <NavBar />}
      <main className="app-main">
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          {pageList.map(({ path, component: Component }) => (
            <Route key={path} path={path} element={<Component />} />
          ))}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <ThemeProvider>
      <Router>
        <AppLayout />
      </Router>
    </ThemeProvider>
  );
}

export default App;