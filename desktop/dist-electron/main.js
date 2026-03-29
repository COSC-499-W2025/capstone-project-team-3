import { ipcMain as v, app as f, BrowserWindow as g, dialog as b } from "electron";
import { fileURLToPath as D } from "node:url";
import s from "node:path";
import _ from "node:fs";
import A from "node:http";
import N from "node:readline";
import { spawn as x } from "node:child_process";
const I = s.dirname(D(import.meta.url));
process.env.APP_ROOT = s.join(I, "..");
const E = process.env.VITE_DEV_SERVER_URL, H = s.join(process.env.APP_ROOT, "dist-electron"), R = s.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = E ? s.join(process.env.APP_ROOT, "public") : R;
let p, i = null, a = null;
const w = "SIDECAR_LISTENING ", h = "http://127.0.0.1:47291";
v.handle("api:getBackendOrigin", () => a);
function y() {
  const e = process.env.DESKTOP_BACKEND_BINARY?.trim();
  if (e)
    return _.existsSync(e) ? e : (console.warn("[electron] DESKTOP_BACKEND_BINARY is set but file not found:", e), null);
  if (f.isPackaged) {
    const n = process.platform === "win32" ? "backend-sidecar.exe" : "backend-sidecar", r = process.platform === "win32" ? "win32" : process.platform === "darwin" ? "darwin" : "linux", t = [
      s.join(process.resourcesPath, "backend", r, n),
      s.join(process.resourcesPath, "backend", n)
    ];
    for (const o of t)
      if (_.existsSync(o)) return o;
  }
  return null;
}
function O(e) {
  return `${e.replace(/\/+$/, "")}/health`;
}
async function P(e, n, r) {
  const t = O(e), o = Date.now() + n;
  for (; Date.now() < o; ) {
    if (await new Promise((c) => {
      const l = A.get(t, (d) => {
        d.resume(), c(d.statusCode === 200);
      });
      l.on("error", () => c(!1)), l.setTimeout(2500, () => {
        l.destroy(), c(!1);
      });
    })) return;
    await new Promise((c) => setTimeout(c, r));
  }
  throw new Error(`Timed out waiting for ${t} (${n}ms). Is the sidecar binary valid?`);
}
function B(e, n) {
  const r = e.stdout;
  return r ? new Promise((t, o) => {
    const u = N.createInterface({ input: r, crlfDelay: 1 / 0 }), c = () => {
      u.close();
    }, l = (m) => {
      clearTimeout(T), u.off("line", d), c(), o(new Error(`Sidecar exited before announcing port (code=${m ?? "unknown"})`));
    }, d = (m) => {
      m.startsWith(w) && (clearTimeout(T), e.removeListener("exit", l), u.off("line", d), c(), t(m.slice(w.length).trim()));
    }, T = setTimeout(() => {
      e.removeListener("exit", l), u.off("line", d), c(), o(new Error(`Timed out after ${n}ms waiting for ${w.trim()} from sidecar`));
    }, n);
    u.on("line", d), e.on("exit", l);
  }) : Promise.reject(new Error("backend-sidecar has no stdout pipe (cannot read SIDECAR_LISTENING)"));
}
function C(e) {
  const n = { ...e };
  if (process.platform !== "darwin")
    return n;
  const r = "/Library/TeX/texbin", t = s.delimiter, o = (n.PATH ?? "").split(t).filter(Boolean);
  return o.includes(r) || (n.PATH = [r, ...o].join(t)), n;
}
function L() {
  if (i && !i.killed)
    return { ok: !0, spawnedNew: !1 };
  const e = y();
  if (!e)
    return console.log(
      "[electron] No backend binary configured. Start the API manually (e.g. uvicorn) or set DESKTOP_BACKEND_BINARY."
    ), a = null, { ok: !1, spawnedNew: !1 };
  const n = s.dirname(e), r = process.env.DESKTOP_BACKEND_DEBUG === "1" || process.env.DESKTOP_BACKEND_DEBUG === "true";
  return i = x(e, [], {
    cwd: n,
    env: {
      ...C(process.env),
      PYTHONUNBUFFERED: "1",
      PROMPT_ROOT: "0",
      AUTO_CONSENT: "true",
      // Sidecar clears resume PDF export cache on SIGTERM/exit (see sidecar_main.py)
      CLEAR_RESUME_PDF_CACHE_ON_EXIT: "1"
    },
    stdio: r ? ["ignore", "pipe", "inherit"] : ["ignore", "pipe", "pipe"]
  }), i.on("exit", (t, o) => {
    console.warn("[electron] backend-sidecar exited", { code: t, signal: o }), i = null, a = null;
  }), !r && i.stderr && i.stderr.on("data", (t) => {
    const o = t.toString();
    o.trim() && console.error("[backend-sidecar]", o.slice(0, 2e3));
  }), console.log("[electron] started backend-sidecar:", e), { ok: !0, spawnedNew: !0 };
}
async function S() {
  const { ok: e, spawnedNew: n } = L();
  if (e) {
    if (n && i)
      try {
        a = await B(i, 2e4), console.log("[electron] sidecar API origin:", a);
      } catch (r) {
        console.warn(
          "[electron] no SIDECAR_LISTENING line in time; probing fixed default port",
          h,
          r instanceof Error ? `(${r.message})` : ""
        );
        try {
          await P(h, 1e5, 400), a = h, console.warn("[electron] sidecar OK via default port (stdout handshake missed)");
        } catch (t) {
          throw console.error("[electron] sidecar did not become ready:", t), i.kill(), i = null, a = null, t;
        }
      }
    else if (!a)
      throw new Error(
        "Sidecar process is running but the listen URL is unknown. Quit the app completely and try again."
      );
    a && await P(a, 12e4, 400);
  }
}
function U() {
  const e = new g({
    width: 420,
    height: 140,
    show: !1,
    frame: !1,
    center: !0,
    resizable: !1,
    alwaysOnTop: !0
  });
  return e.loadURL(
    `data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html><html><body style="margin:0;font-family:system-ui,-apple-system,sans-serif;background:#1e1e1e;color:#e0e0e0;display:flex;align-items:center;justify-content:center;height:100vh;font-size:14px;">
      <div style="text-align:center;padding:1.25rem;">
        <div style="margin-bottom:0.5rem">Starting backend…</div>
        <div style="opacity:0.75;font-size:12px">First launch may take a minute.</div>
      </div></body></html>`)}`
  ), e.once("ready-to-show", () => e.show()), e;
}
function k() {
  p = new g({
    title: "Big Picture",
    icon: s.join(process.env.VITE_PUBLIC, "big-picture-icon.png"),
    webPreferences: {
      preload: s.join(I, "preload.mjs")
    }
  }), p.webContents.on("did-finish-load", () => {
    p?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), E ? p.loadURL(E) : p.loadFile(s.join(R, "index.html"));
}
f.on("window-all-closed", () => {
  process.platform !== "darwin" && (f.quit(), p = null);
});
f.on("activate", () => {
  g.getAllWindows().length === 0 && (async () => {
    if (y())
      try {
        await S();
      } catch (e) {
        console.error("[electron]", e), b.showMessageBox({
          type: "error",
          title: "Backend not ready",
          message: "The local API server did not become ready in time.",
          detail: e instanceof Error ? e.message : String(e)
        });
        return;
      }
    k();
  })();
});
f.on("before-quit", () => {
  i && !i.killed && (i.kill(), i = null);
});
f.whenReady().then(async () => {
  let e = null;
  if (y()) {
    e = U();
    try {
      await S();
    } catch (n) {
      console.error("[electron]", n), e?.destroy(), b.showMessageBox({
        type: "error",
        title: "Backend not ready",
        message: "The local API server did not become ready in time.",
        detail: n instanceof Error ? n.message : String(n)
      }), f.quit();
      return;
    }
    e?.destroy();
  }
  k();
});
export {
  H as MAIN_DIST,
  R as RENDERER_DIST,
  E as VITE_DEV_SERVER_URL
};
