import { ipcMain as N, app as u, BrowserWindow as g, dialog as P } from "electron";
import { fileURLToPath as v } from "node:url";
import s from "node:path";
import y from "node:fs";
import I from "node:http";
import O from "node:readline";
import { spawn as C } from "node:child_process";
const R = s.dirname(v(import.meta.url));
process.env.APP_ROOT = s.join(R, "..");
const E = process.env.VITE_DEV_SERVER_URL, X = s.join(process.env.APP_ROOT, "dist-electron"), D = s.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = E ? s.join(process.env.APP_ROOT, "public") : D;
let p, i = null, a = null;
const w = "SIDECAR_LISTENING ", h = 8e3, _ = 8099, B = 12e4, x = 6e5;
N.handle("api:getBackendOrigin", () => a);
function T() {
  const e = process.env.DESKTOP_BACKEND_BINARY?.trim();
  if (e)
    return y.existsSync(e) ? e : (console.warn("[electron] DESKTOP_BACKEND_BINARY is set but file not found:", e), null);
  if (u.isPackaged) {
    const n = process.platform === "win32" ? "backend-sidecar.exe" : "backend-sidecar", t = process.platform === "win32" ? "win32" : process.platform === "darwin" ? "darwin" : "linux", o = [
      s.join(process.resourcesPath, "backend", t, n),
      s.join(process.resourcesPath, "backend", n)
    ];
    for (const r of o)
      if (y.existsSync(r)) return r;
  }
  return null;
}
function A(e) {
  return `${e.replace(/\/+$/, "")}/health`;
}
async function L(e, n, t) {
  const o = A(e), r = Date.now() + n;
  for (; Date.now() < r; ) {
    if (await new Promise((c) => {
      const l = I.get(o, (d) => {
        d.resume(), c(d.statusCode === 200);
      });
      l.on("error", () => c(!1)), l.setTimeout(2500, () => {
        l.destroy(), c(!1);
      });
    })) return;
    await new Promise((c) => setTimeout(c, t));
  }
  throw new Error(`Timed out waiting for ${o} (${n}ms). Is the sidecar binary valid?`);
}
function U(e, n) {
  return new Promise((t) => {
    const o = I.get(A(e), (r) => {
      r.resume(), t(r.statusCode === 200);
    });
    o.on("error", () => t(!1)), o.setTimeout(n, () => {
      o.destroy(), t(!1);
    });
  });
}
async function $(e) {
  const n = Date.now() + e;
  for (; Date.now() < n; ) {
    for (let t = h; t <= _; t++) {
      const o = `http://127.0.0.1:${t}`;
      if (await U(o, 120))
        return o;
    }
    await new Promise((t) => setTimeout(t, 350));
  }
  return null;
}
function K(e, n) {
  const t = e.stdout;
  return t ? new Promise((o, r) => {
    const f = O.createInterface({ input: t, crlfDelay: 1 / 0 }), c = () => {
      f.close();
    }, l = (m) => {
      clearTimeout(S), f.off("line", d), c(), r(new Error(`Sidecar exited before announcing port (code=${m ?? "unknown"})`));
    }, d = (m) => {
      m.startsWith(w) && (clearTimeout(S), e.removeListener("exit", l), f.off("line", d), c(), o(m.slice(w.length).trim()));
    }, S = setTimeout(() => {
      e.removeListener("exit", l), f.off("line", d), c(), r(new Error(`Timed out after ${n}ms waiting for ${w.trim()} from sidecar`));
    }, n);
    f.on("line", d), e.on("exit", l);
  }) : Promise.reject(new Error("backend-sidecar has no stdout pipe (cannot read SIDECAR_LISTENING)"));
}
function j(e) {
  const n = { ...e };
  if (process.platform !== "darwin")
    return n;
  const t = "/Library/TeX/texbin", o = s.delimiter, r = (n.PATH ?? "").split(o).filter(Boolean);
  return r.includes(t) || (n.PATH = [t, ...r].join(o)), n;
}
function H() {
  if (i && !i.killed)
    return { ok: !0, spawnedNew: !1 };
  const e = T();
  if (!e)
    return console.log(
      "[electron] No backend binary configured. Start the API manually (e.g. uvicorn) or set DESKTOP_BACKEND_BINARY."
    ), a = null, { ok: !1, spawnedNew: !1 };
  const n = s.dirname(e), t = process.env.DESKTOP_BACKEND_DEBUG === "1" || process.env.DESKTOP_BACKEND_DEBUG === "true";
  return i = C(e, [], {
    cwd: n,
    env: {
      ...j(process.env),
      PYTHONUNBUFFERED: "1",
      PROMPT_ROOT: "0",
      AUTO_CONSENT: "true",
      // Sidecar clears resume PDF export cache on SIGTERM/exit (see sidecar_main.py)
      CLEAR_RESUME_PDF_CACHE_ON_EXIT: "1"
    },
    stdio: t ? ["ignore", "pipe", "inherit"] : ["ignore", "pipe", "pipe"]
  }), i.on("exit", (o, r) => {
    console.warn("[electron] backend-sidecar exited", { code: o, signal: r }), i = null, a = null;
  }), !t && i.stderr && i.stderr.on("data", (o) => {
    const r = o.toString();
    r.trim() && console.error("[backend-sidecar]", r.slice(0, 2e3));
  }), console.log("[electron] started backend-sidecar:", e), { ok: !0, spawnedNew: !0 };
}
async function b() {
  const { ok: e, spawnedNew: n } = H();
  if (e) {
    if (n && i)
      try {
        a = await K(i, B), console.log("[electron] sidecar API origin:", a);
      } catch (t) {
        console.warn(
          "[electron] no SIDECAR_LISTENING line in time; scanning",
          `${h}-${_}`,
          t instanceof Error ? `(${t.message})` : ""
        );
        const o = await $(12e4);
        if (o)
          a = o, console.warn("[electron] sidecar OK via port scan (stdout handshake missed)");
        else
          throw console.error("[electron] sidecar not found on scanned ports"), i.kill(), i = null, a = null, new Error(
            `No SIDECAR_LISTENING line and no /health on 127.0.0.1:${h}-${_}. Rebuild the sidecar or set DESKTOP_BACKEND_DEBUG=1.`
          );
      }
    else if (!a)
      throw new Error(
        "Sidecar process is running but the listen URL is unknown. Quit the app completely and try again."
      );
    a && await L(a, x, 400);
  }
}
function V() {
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
      preload: s.join(R, "preload.mjs")
    }
  }), p.webContents.on("did-finish-load", () => {
    p?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), E ? p.loadURL(E) : p.loadFile(s.join(D, "index.html"));
}
u.on("window-all-closed", () => {
  process.platform !== "darwin" && (u.quit(), p = null);
});
u.on("activate", () => {
  g.getAllWindows().length === 0 && (async () => {
    if (T())
      try {
        await b();
      } catch (e) {
        console.error("[electron]", e), P.showMessageBox({
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
u.on("before-quit", () => {
  i && !i.killed && (i.kill(), i = null);
});
u.whenReady().then(async () => {
  let e = null;
  if (T()) {
    e = V();
    try {
      await b();
    } catch (n) {
      console.error("[electron]", n), e?.destroy(), P.showMessageBox({
        type: "error",
        title: "Backend not ready",
        message: "The local API server did not become ready in time.",
        detail: n instanceof Error ? n.message : String(n)
      }), u.quit();
      return;
    }
    e?.destroy();
  }
  k();
});
export {
  X as MAIN_DIST,
  D as RENDERER_DIST,
  E as VITE_DEV_SERVER_URL
};
