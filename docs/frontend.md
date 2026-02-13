# Prerequisites

## Node.js Version
This project requires **Node.js 21+** due to dependencies that are only compatible with newer Node.js versions:
- `vite@^7.3.1` requires Node.js 21+
- `electron@^40.2.1` requires Node.js 21+

To check your Node.js version:
```bash
node --version
```

If you need to upgrade, download the latest version from [nodejs.org](https://nodejs.org/) or use a version manager like [nvm](https://github.com/nvm-sh/nvm).

# How to Run FrontEnd with Current Env

1. In your terminal, run `docker compose up --build`.
2. In another terminal window, run `cd desktop`.
3. If this is your first time loading frontend, run `npm install`.
4. Load env by running `npm run dev`.
5. You should see an application load. After it has loaded, you should see `Backend status: ok`.

# Adding a New Desktop Page

1. Copy `desktop/src/api/template.ts` → `desktop/src/api/myEndpoint.ts`
2. Update `ENDPOINT_HERE` with your backend route
3. Copy `desktop/src/pages/TemplatePage.tsx` → `desktop/src/pages/MyPage.tsx` still within the pages folder
4. Import your new API client in the page
5. Automatically, the page shows up in `App.tsx`, no need of adding the link yourself.
6. Run `npm run dev` to test
7. Confirm backend is running

# Creating Tests for a New Page

1. Create a new test file in `desktop/tests/` named after your page, e.g. `MyPage.test.tsx`.
2. Import your page component and the API client.
3. Mock the API client using `jest.mock` to simulate backend responses.
4. Write tests for:

   * Rendering the page
   * Button clicks / user interactions
   * Displaying data returned from the mocked API
   * Error handling
5. Run `npm run test` to verify tests pass.

# Troubleshooting

If you see `error failed` on loading `npm run dev`, try loading `http://localhost:8000/health` in your browser.

If status is ok:
```
{"status":"ok"}
```
Then issue is a middleware problem. Check CORS connection in `app/main.py`.

If status is not ok:
- Ensure `docker compose up --build` is running. Then check localhost link mentioned above.


# Future Pending (Once UI is in Full Swing)

1. **E2E Testing**

   * Incorporate Playwright or Spectron for full app flows once most UI is stable.
   * Test things like “click Run → data displays → window closes.”

2. **Remove temporary nav bar**

   * The nav is for dev/testing only.
   * Replace with proper routing / final UI navigation later.

3. **Integrate frontend + backend startup**

   * Eventually, make `npm run dev` optionally start Docker automatically.
   * Could use scripts or Electron preload logic.

4. **Dynamic page routing improvements**

   * Right now paths are based on filenames.
   * Consider mapping friendly routes and titles (e.g., `/user-list` instead of `/UserList.tsx`).

5. **Styling / UI consistency**

   * Set up a shared component library (buttons, cards, modals).
   * Consider a CSS framework / Tailwind / design system.

6. **Backend mocking for frontend tests**

   * Use MSW to simulate backend responses for frontend dev and CI.
   * Reduces dependency on Docker backend for testing.

7. **Production packaging**

   * Plan how to build a distributable Electron app (`.exe`, `.dmg`, `.AppImage`).
   * Integrate production build with backend or remote API.

8. **Code quality / linting**

   * Add ESLint / Prettier for consistent code style across team.
   * Run linting in CI.