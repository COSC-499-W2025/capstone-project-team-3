import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { pageList } from "./pages";
import WelcomePage from "./pages/WelcomePage";
import { getHealth } from "./api/health";
import { useState, useEffect } from "react";
import { NavBar } from "./NavBar";

function App() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <Router>
      <div className="app-layout">
        <NavBar />
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
    </Router>
  );
}

export default App;