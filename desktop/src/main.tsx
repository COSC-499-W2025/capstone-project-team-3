import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./styles/dark-theme.css";
import { initApiBaseUrlFromElectron } from "./config/api";

void (async () => {
  await initApiBaseUrlFromElectron();

  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );

  if (typeof window !== "undefined" && window.ipcRenderer) {
    window.ipcRenderer.on("main-process-message", (_event, message) => {
      console.log(message);
    });
  }
})();
