import { useNavigate } from "react-router-dom";
import "../styles/WelcomePage.css";

/**
 * Welcome/Landing Page - First page users see
 */
export function WelcomePage() {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/uploadpage");
  };

  return (
    <div className="welcome-container" onClick={handleClick}>
      <div className="welcome-frame welcome-frame-1">
        <div className="welcome-frame welcome-frame-2">
          <div className="welcome-frame welcome-frame-3">
            <div className="welcome-frame welcome-frame-4">
              <h1 className="welcome-title">Welcome to your Big Picture</h1>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WelcomePage;
