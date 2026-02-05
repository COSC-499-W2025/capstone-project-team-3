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
