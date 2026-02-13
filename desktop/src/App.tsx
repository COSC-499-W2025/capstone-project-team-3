import { BrowserRouter as Router, Routes, Route, Navigate, Link } from "react-router-dom";
import { pageList } from "./pages";
import WelcomePage from "./pages/WelcomePage";
import { getHealth } from "./api/health";
import { useState, useEffect } from "react";

function App() {
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((data) => setStatus(data.status))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <Router>
      <nav style={{ padding: 10, borderBottom: "1px solid #ccc" }}>
        <Link to="/" style={{ marginRight: 10 }}>Home</Link>
        {pageList.map(({ path }) => (
          <Link key={path} to={path} style={{ marginRight: 10 }}>
            {path.replace('/', '')}
          </Link>
        ))}
        <span style={{ marginLeft: "auto", opacity: 0.7, fontSize: "0.9em" }} title={error ?? undefined}>{status}</span>
        </nav>
      <div>
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          {pageList.map(({ path, component: Component }) => (
            <Route key={path} path={path} element={<Component />} />
          ))}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;