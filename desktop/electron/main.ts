import { app, BrowserWindow } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import http from 'node:http'
import { spawn, type ChildProcess } from 'node:child_process'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
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

async function waitForHealth(timeoutMs: number, intervalMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const ok = await new Promise<boolean>((resolve) => {
      const req = http.get('http://127.0.0.1:8000/health', (res) => {
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
  throw new Error(
    `Timed out waiting for http://127.0.0.1:8000/health (${timeoutMs}ms). Is the sidecar binary valid?`
  )
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

function startBackendSidecar(): boolean {
  if (backendChild && !backendChild.killed) return true

  const exe = resolveBackendExecutable()
  if (!exe) {
    console.log(
      '[electron] No backend binary configured. Start Docker or run the sidecar manually on port 8000, or set DESKTOP_BACKEND_BINARY.'
    )
    return false
  }

  const cwd = path.dirname(exe)
  const debug = process.env.DESKTOP_BACKEND_DEBUG === '1' || process.env.DESKTOP_BACKEND_DEBUG === 'true'

  backendChild = spawn(exe, [], {
    cwd,
    env: {
      ...envWithTexPath(process.env),
      PROMPT_ROOT: '0',
      AUTO_CONSENT: 'true',
    },
    stdio: debug ? 'inherit' : 'pipe',
  })

  backendChild.on('exit', (code, signal) => {
    console.warn('[electron] backend-sidecar exited', { code, signal })
    backendChild = null
  })

  if (!debug && backendChild.stderr) {
    backendChild.stderr.on('data', (chunk: Buffer) => {
      const s = chunk.toString()
      if (s.trim()) console.error('[backend-sidecar]', s.slice(0, 2000))
    })
  }

  console.log('[electron] started backend-sidecar:', exe)
  return true
}

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
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
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('before-quit', () => {
  if (backendChild && !backendChild.killed) {
    backendChild.kill()
    backendChild = null
  }
})

app.whenReady().then(async () => {
  if (startBackendSidecar()) {
    try {
      await waitForHealth(120_000, 400)
    } catch (err) {
      console.error('[electron]', err)
    }
  }
  createWindow()
})
