import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { getHealth } from "./api/health";
import { pageList } from "./pages";

function App() {
  const [status, setStatus] = useState("loading...");
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
      </nav>

      <div style={{ padding: 20 }}>
        <Routes>
          <Route path="/" element={
            <>
            <h1>Welcome to Desktop App</h1>
            <p>Backend status: <b>{status}</b></p>
            </>
        } />
          {pageList.map(({ path, component: Component }) => (
            <Route key={path} path={path} element={<Component />} />
          ))}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
