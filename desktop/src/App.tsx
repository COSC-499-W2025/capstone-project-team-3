import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { pageList } from "./pages";
import WelcomePage from "./pages/WelcomePage";

function App() {
  return (
    <Router>
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
