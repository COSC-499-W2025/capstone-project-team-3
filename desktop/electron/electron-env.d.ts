/// <reference types="vite-plugin-electron/electron-env" />

declare namespace NodeJS {
  interface ProcessEnv {
    /**
     * The built directory structure
     *
     * ```tree
     * ├─┬─┬ dist
     * │ │ └── index.html
     * │ │
     * │ ├─┬ dist-electron
     * │ │ ├── main.js
     * │ │ └── preload.js
     * │
     * ```
     */
    APP_ROOT: string
    /** /dist/ or /public/ */
    VITE_PUBLIC: string
    /** Absolute path to PyInstaller backend-sidecar binary (dev: point at dist/backend-sidecar/...) */
    DESKTOP_BACKEND_BINARY?: string
    /** If set, backend child inherits stdio (verbose logs in terminal) */
    DESKTOP_BACKEND_DEBUG?: string
    /** Optional full path to pdflatex when not on PATH (passed through to sidecar) */
    PDFLATEX_PATH?: string
  }
}

// Used in Renderer process, expose in `preload.ts`
interface Window {
  ipcRenderer: import('electron').IpcRenderer
}
