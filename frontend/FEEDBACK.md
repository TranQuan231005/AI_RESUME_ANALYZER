# Action feedback

The frontend keeps the existing API contracts, authentication and result routes.
Run Match opens a native modal dialog with a CV scan animation. The percent is an
estimate: 65% at 10 seconds, 85% at 30 seconds, and at most 95% while the request
is pending. Only a successful response produces 100%, followed by a 400 ms
completion state before navigation. A slow request can be minimized after 60
seconds. Minimizing does not cancel or repeat a request.

Errors stop progress and offer Close / Try again while retaining the inputs.
401 responses follow the existing logout route. Request guards prevent repeated
submissions and ignore stale responses after unmount or a session change. Timers
and scroll locks are cleaned up. Reduced-motion preferences disable the decorative
animations. Other actions use local feedback: busy buttons, a scoring status,
file selection/drag states, readable skeletons, and history/Admin retry states.

## Verification

Run from `frontend` (use `npm.cmd` in Windows PowerShell if script policy blocks npm):

```text
npm test -- --runInBand
npm run lint
npm run build
```

The browser smoke script uses a fresh headless Chrome profile and intercepts all
API requests with contract fixtures. It does not require or call the backend.
Playwright is installed separately under ignored `node_modules`, not added to
application dependencies:

```text
npm install --prefix node_modules/.browser-check --no-save --package-lock=false --ignore-scripts --no-audit --no-fund playwright
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
node scripts/feedback-smoke.cjs
```

Chrome must be installed. Screenshots are written to
`node_modules/.browser-check/artifacts`. Tests cover 320/768/1024/1440 px,
native modal behavior, reduced motion, delayed requests, minimizing, retries,
PDF/text JD input, scoring, 401 handling, history, Admin and logout. Expected
401/503 console messages from deliberately failed API requests are distinguished
from unexpected errors. This verifies frontend behavior, not AI service latency.

The baseline before changes passed 41 tests, TypeScript and the production build.
After implementation, all 53 tests, TypeScript, production build and the Chrome
smoke scenarios passed. The browser run needs network access for the existing
Google Fonts stylesheet in `index.html`; restricted environments can block that
resource independently of the frontend changes.
No database migration or backend deployment is needed; the feedback changes can
be reverted within the frontend.
