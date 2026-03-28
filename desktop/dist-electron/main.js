import { app as e, BrowserWindow as s } from "electron";
import { fileURLToPath as a } from "node:url";
import o from "node:path";
const t = o.dirname(a(import.meta.url));
e.setName("Big Picture");
process.platform === "win32" && e.setAppUserModelId("com.bigpicture.app");
process.env.APP_ROOT = o.join(t, "..");
const i = process.env.VITE_DEV_SERVER_URL, w = o.join(process.env.APP_ROOT, "dist-electron"), r = o.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = i ? o.join(process.env.APP_ROOT, "public") : r;
const c = o.join(process.env.VITE_PUBLIC, "app-icon.png");
let n;
function p() {
  n = new s({
    icon: c,
    webPreferences: {
      preload: o.join(t, "preload.mjs")
    }
  }), n.webContents.on("did-finish-load", () => {
    n?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), i ? n.loadURL(i) : n.loadFile(o.join(r, "index.html"));
}
e.on("window-all-closed", () => {
  process.platform !== "darwin" && (e.quit(), n = null);
});
e.on("activate", () => {
  s.getAllWindows().length === 0 && p();
});
e.whenReady().then(() => {
  process.platform === "darwin" && e.dock && e.dock.setIcon(c), p();
});
export {
  w as MAIN_DIST,
  r as RENDERER_DIST,
  i as VITE_DEV_SERVER_URL
};
