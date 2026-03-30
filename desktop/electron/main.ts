import { app, BrowserWindow, dialog, ipcMain } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import http from 'node:http'
import readline from 'node:readline'
import { spawn, spawnSync, type ChildProcess } from 'node:child_process'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null
let backendChild: ChildProcess | null = null
/** Set when this process spawned the sidecar and parsed `SIDECAR_LISTENING` from its stdout. */
let backendApiOrigin: string | null = null

const SIDECAR_LISTEN_PREFIX = 'SIDECAR_LISTENING '

/** Must stay in sync with sidecar defaults for `SIDECAR_PORT_SCAN_LO` / `SIDECAR_PORT_SCAN_HI`. */
const SIDECAR_PORT_SCAN_LO = 8000
const SIDECAR_PORT_SCAN_HI = 8099

/** PyInstaller can delay stdout; cold imports happen after the port line is printed. */
const SIDECAR_STDOUT_LINE_MS = 120_000
const SIDECAR_HEALTH_WAIT_MS = 600_000

ipcMain.handle('api:getBackendOrigin', () => backendApiOrigin)

function resolveBackendExecutable(): string | null {
  const fromEnv = process.env.DESKTOP_BACKEND_BINARY?.trim()
  if (fromEnv) {
    if (fs.existsSync(fromEnv)) return fromEnv
    console.warn('[electron] DESKTOP_BACKEND_BINARY is set but file not found:', fromEnv)
    return null
  }

  if (app.isPackaged) {
    const name = process.platform === 'win32' ? 'backend-sidecar.exe' : 'backend-sidecar'
    const platformDir =
      process.platform === 'win32' ? 'win32' : process.platform === 'darwin' ? 'darwin' : 'linux'
    const candidates = [
      path.join(process.resourcesPath, 'backend', platformDir, name),
      path.join(process.resourcesPath, 'backend', name),
    ]
    for (const p of candidates) {
      if (fs.existsSync(p)) return p
    }
  }

  return null
}

/**
 * Best-effort self-heal for macOS packaged apps:
 * - Ensure sidecar has execute bit
 * - Remove quarantine xattr from app bundle and sidecar so Gatekeeper does not block spawn
 */
function repairPackagedMacSidecarPermissions(exe: string): void {
  if (!(app.isPackaged && process.platform === 'darwin')) {
    return
  }

  try {
    fs.chmodSync(exe, 0o755)
  } catch (err) {
    console.warn('[electron] chmod sidecar failed:', err)
  }

  const appBundlePath = path.resolve(process.resourcesPath, '..', '..')
  const xattrBin = '/usr/bin/xattr'
  if (!fs.existsSync(xattrBin)) {
    return
  }

  // Clear quarantine recursively on the app bundle first, then directly on sidecar.
  const clearTargets = [
    ['-dr', 'com.apple.quarantine', appBundlePath],
    ['-d', 'com.apple.quarantine', exe],
  ]

  for (const args of clearTargets) {
    try {
      const result = spawnSync(xattrBin, args, { timeout: 7000 })
      if (result.error) {
        console.warn('[electron] xattr clear failed:', { args, error: result.error.message })
      }
    } catch (err) {
      console.warn('[electron] xattr clear exception:', { args, err })
    }
  }
}

function healthUrl(origin: string): string {
  return `${origin.replace(/\/+$/, '')}/health`
}

async function waitForHealth(
  origin: string,
  timeoutMs: number,
  intervalMs: number
): Promise<void> {
  const url = healthUrl(origin)
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const ok = await new Promise<boolean>((resolve) => {
      const req = http.get(url, (res) => {
        res.resume()
        resolve(res.statusCode === 200)
      })
      req.on('error', () => resolve(false))
      req.setTimeout(2500, () => {
        req.destroy()
        resolve(false)
      })
    })
    if (ok) return
    await new Promise((r) => setTimeout(r, intervalMs))
  }
  throw new Error(`Timed out waiting for ${url} (${timeoutMs}ms). Is the sidecar binary valid?`)
}

function healthCheckOnce(origin: string, reqTimeoutMs: number): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(healthUrl(origin), (res) => {
      res.resume()
      resolve(res.statusCode === 200)
    })
    req.on('error', () => resolve(false))
    req.setTimeout(reqTimeoutMs, () => {
      req.destroy()
      resolve(false)
    })
  })
}

/**
 * If `SIDECAR_LISTENING` is missed (buffering / old binary), find the sidecar by polling /health
 * on the same port range the Python process scans.
 */
async function discoverSidecarOriginByPortScan(totalTimeoutMs: number): Promise<string | null> {
  const deadline = Date.now() + totalTimeoutMs
  while (Date.now() < deadline) {
    for (let p = SIDECAR_PORT_SCAN_LO; p <= SIDECAR_PORT_SCAN_HI; p++) {
      const origin = `http://127.0.0.1:${p}`
      if (await healthCheckOnce(origin, 120)) {
        return origin
      }
    }
    await new Promise((r) => setTimeout(r, 350))
  }
  return null
}

function awaitSidecarListenLine(child: ChildProcess, timeoutMs: number): Promise<string> {
  const stdout = child.stdout
  if (!stdout) {
    return Promise.reject(new Error('backend-sidecar has no stdout pipe (cannot read SIDECAR_LISTENING)'))
  }
  return new Promise((resolve, reject) => {
    const rl = readline.createInterface({ input: stdout, crlfDelay: Infinity })

    const cleanup = () => {
      rl.close()
    }

    const onExit = (code: string | number | null) => {
      clearTimeout(timer)
      rl.off('line', onLine)
      cleanup()
      reject(new Error(`Sidecar exited before announcing port (code=${code ?? 'unknown'})`))
    }

    const onLine = (line: string) => {
      if (line.startsWith(SIDECAR_LISTEN_PREFIX)) {
        clearTimeout(timer)
        child.removeListener('exit', onExit)
        rl.off('line', onLine)
        cleanup()
        resolve(line.slice(SIDECAR_LISTEN_PREFIX.length).trim())
      }
    }

    const timer = setTimeout(() => {
      child.removeListener('exit', onExit)
      rl.off('line', onLine)
      cleanup()
      reject(new Error(`Timed out after ${timeoutMs}ms waiting for ${SIDECAR_LISTEN_PREFIX.trim()} from sidecar`))
    }, timeoutMs)

    rl.on('line', onLine)
    child.on('exit', onExit)
  })
}

/**
 * macOS GUI apps inherit a minimal PATH; BasicTeX/MacTeX install pdflatex under here.
 * Prepend so resume/cover-letter PDF export finds `pdflatex` without a shell login session.
 */
function envWithTexPath(env: NodeJS.ProcessEnv): NodeJS.ProcessEnv {
  const out = { ...env }
  if (process.platform !== 'darwin') {
    return out
  }
  const texBin = '/Library/TeX/texbin'
  const sep = path.delimiter
  const parts = (out.PATH ?? '').split(sep).filter(Boolean)
  if (!parts.includes(texBin)) {
    out.PATH = [texBin, ...parts].join(sep)
  }
  return out
}

/**
 * Spawns the PyInstaller sidecar when a bundled binary exists.
 * Returns `{ ok, spawnedNew }`: `ok` is false if no bundled binary; `spawnedNew` is true when a new
 * process was started (caller must read `SIDECAR_LISTENING` from stdout).
 */
function startBackendSidecar(): { ok: boolean; spawnedNew: boolean } {
  if (backendChild && !backendChild.killed) {
    return { ok: true, spawnedNew: false }
  }

  const exe = resolveBackendExecutable()
  if (!exe) {
    console.log(
      '[electron] No backend binary configured. Start the API manually (e.g. uvicorn) or set DESKTOP_BACKEND_BINARY.'
    )
    backendApiOrigin = null
    return { ok: false, spawnedNew: false }
  }

  const cwd = path.dirname(exe)
  const debug = process.env.DESKTOP_BACKEND_DEBUG === '1' || process.env.DESKTOP_BACKEND_DEBUG === 'true'

  repairPackagedMacSidecarPermissions(exe)

  // Keep stdout piped so we can parse SIDECAR_LISTENING; in debug mode send sidecar stderr to terminal.
  backendChild = spawn(exe, [], {
    cwd,
    env: {
      ...envWithTexPath(process.env),
      PYTHONUNBUFFERED: '1',
      PROMPT_ROOT: '0',
      AUTO_CONSENT: 'true',
      // Sidecar clears resume PDF export cache on SIGTERM/exit (see sidecar_main.py)
      CLEAR_RESUME_PDF_CACHE_ON_EXIT: '1',
    },
    stdio: debug ? ['ignore', 'pipe', 'inherit'] : ['ignore', 'pipe', 'pipe'],
  })

  backendChild.on('exit', (code, signal) => {
    console.warn('[electron] backend-sidecar exited', { code, signal })
    backendChild = null
    backendApiOrigin = null
  })

  if (!debug && backendChild.stderr) {
    backendChild.stderr.on('data', (chunk: Buffer) => {
      const s = chunk.toString()
      if (s.trim()) console.error('[backend-sidecar]', s.slice(0, 2000))
    })
  }

  console.log('[electron] started backend-sidecar:', exe)
  return { ok: true, spawnedNew: true }
}

async function ensureManagedSidecarReady(): Promise<void> {
  const { ok, spawnedNew } = startBackendSidecar()
  if (!ok) {
    return
  }
  if (spawnedNew && backendChild) {
    try {
      backendApiOrigin = await awaitSidecarListenLine(backendChild, SIDECAR_STDOUT_LINE_MS)
      console.log('[electron] sidecar API origin:', backendApiOrigin)
    } catch (err) {
      console.warn(
        '[electron] no SIDECAR_LISTENING line in time; scanning',
        `${SIDECAR_PORT_SCAN_LO}-${SIDECAR_PORT_SCAN_HI}`,
        err instanceof Error ? `(${err.message})` : ''
      )
      const discovered = await discoverSidecarOriginByPortScan(120_000)
      if (discovered) {
        backendApiOrigin = discovered
        console.warn('[electron] sidecar OK via port scan (stdout handshake missed)')
      } else {
        console.error('[electron] sidecar not found on scanned ports')
        backendChild.kill()
        backendChild = null
        backendApiOrigin = null
        throw new Error(
          `No SIDECAR_LISTENING line and no /health on 127.0.0.1:${SIDECAR_PORT_SCAN_LO}-${SIDECAR_PORT_SCAN_HI}. Rebuild the sidecar or set DESKTOP_BACKEND_DEBUG=1.`
        )
      }
    }
  } else if (!backendApiOrigin) {
    throw new Error(
      'Sidecar process is running but the listen URL is unknown. Quit the app completely and try again.'
    )
  }
  if (!backendApiOrigin) {
    return
  }
  await waitForHealth(backendApiOrigin, SIDECAR_HEALTH_WAIT_MS, 400)
}

/** Small window while waiting for FastAPI /health (sidecar can take tens of seconds on cold start). */
function createSplashWindow(): BrowserWindow {
  const splash = new BrowserWindow({
    width: 420,
    height: 140,
    show: false,
    frame: false,
    center: true,
    resizable: false,
    alwaysOnTop: true,
  })
  void splash.loadURL(
    `data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html><html><body style="margin:0;font-family:system-ui,-apple-system,sans-serif;background:#1e1e1e;color:#e0e0e0;display:flex;align-items:center;justify-content:center;height:100vh;font-size:14px;">
      <div style="text-align:center;padding:1.25rem;">
        <div style="margin-bottom:0.5rem">Starting backend…</div>
        <div style="opacity:0.75;font-size:12px">First launch may take a minute.</div>
      </div></body></html>`)}`
  )
  splash.once('ready-to-show', () => splash.show())
  return splash
}

function createWindow() {
  win = new BrowserWindow({
    title: 'Big Picture',
    icon: path.join(process.env.VITE_PUBLIC, 'big-picture-icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
    },
  })

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', new Date().toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

// Quit when all windows are closed, except on macOS. There, it's common
// for the application and its menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  // On OS X it's common to re-create a window when the dock icon is clicked.
  if (BrowserWindow.getAllWindows().length === 0) {
    void (async () => {
      if (resolveBackendExecutable()) {
        try {
          await ensureManagedSidecarReady()
        } catch (err) {
          console.error('[electron]', err)
          void dialog.showMessageBox({
            type: 'error',
            title: 'Backend not ready',
            message: 'The local API server did not become ready in time.',
            detail: err instanceof Error ? err.message : String(err),
          })
          return
        }
      }
      createWindow()
    })()
  }
})

app.on('before-quit', () => {
  if (backendChild && !backendChild.killed) {
    backendChild.kill()
    backendChild = null
  }
})

app.whenReady().then(async () => {
  let splash: BrowserWindow | null = null
  if (resolveBackendExecutable()) {
    splash = createSplashWindow()
    try {
      await ensureManagedSidecarReady()
    } catch (err) {
      console.error('[electron]', err)
      splash?.destroy()
      void dialog.showMessageBox({
        type: 'error',
        title: 'Backend not ready',
        message: 'The local API server did not become ready in time.',
        detail: err instanceof Error ? err.message : String(err),
      })
      app.quit()
      return
    }
    splash?.destroy()
  }

  createWindow()
})
