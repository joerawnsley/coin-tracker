# Improvements Plan

This file tracks a prioritized list of improvements identified during a codebase review, to be tackled one at a time.

## Background

Full review findings (for context, not all in scope immediately):

### Critical (correctness/security bugs)
1. **Unhandled "not found" errors -> 500s everywhere.** Every `Coin.get(...)` / `Duty.get(...)` call raises `peewee.DoesNotExist` if the record isn't found, which FastAPI turns into a raw 500. Documented in README's own "known issues".
2. **Duplicate-record creation -> 500s.** `add_coin`/`add_duty` don't catch `IntegrityError` on unique constraint violations, unlike `delete_coin` which does.
3. **Missing authorization check.** `mark_coin_complete`/`mark_coin_incomplete` authenticate the user but never check `user.role == "admin"`, unlike every other mutating endpoint.
4. **Basic-auth crash path.** If a caller sends no `access_token` and no Basic Auth header, `credentials` is `None`, and `credentials.username` raises an unhandled `AttributeError` -> 500 instead of a clean 401.
5. **JWTs never expire.** No `exp` claim on the encoded JWT. `get_user_from_token` doesn't catch `jwt.ExpiredSignatureError`/`InvalidTokenError` either.
6. **Access tokens accepted as a query parameter** on API routes - gets logged in server/proxy access logs and browser history.

### High-value structural refactor
7. **Massive duplication of the auth block** copy-pasted into 8+ endpoints in `coins_api.py`. Extracting into FastAPI dependencies would prevent bugs like #3.
8. **coins_ui.py calls coins_api.py functions directly as plain Python calls**, re-deriving the user from the token multiple times per request, and several POST handlers don't catch `HTTPException` from `get_user_from_token` consistently.

### Medium
9. **HTTP status codes/response shapes are inconsistent** (plain strings on error, 401 used for both auth and authz failures instead of 403 for the latter).
10. **`database.py` hardcodes the Postgres db/user name (`"joe"`)** rather than reading from env.
11. **No pydantic-settings/config validation layer** - env vars read ad hoc via `os.getenv`.
12. **Duty deletion logs status `"unauthorized"`** for what's actually a deliberate business rule.

### Lower priority / polish
- No pagination on `/api/coins`, `/api/duties`, or `/user-requests`.
- `coin_to_dict`/`duty_to_dict` return Python `set`s - non-deterministic ordering.
- No DB migration tool.
- Stray placeholder comment in README.

---

## Active Plan: Global error handling for "not found" and "duplicate" cases

Fixes 3 documented README gaps via centralized exception handlers instead of scattering try/except blocks across every route.

### Step 1 - DONE
Add a global exception handler for `peewee.DoesNotExist` in `src/app.py` so that any route calling `Coin.get(...)` / `Duty.get(...)` on a missing record returns a clean `404` instead of a raw `500`.

- Add `@app.exception_handler(DoesNotExist)` returning `JSONResponse(status_code=404, ...)`.
- Use a friendlier per-model message if easily derivable (e.g. from `exc.__class__.__qualname__` -> "Coin.DoesNotExist" / "Duty.DoesNotExist").
- No changes needed to existing route logic - `single_coin`, `single_duty`, `add_duties_to_coin`, `remove_duties_from_coin`, `mark_coin_complete/incomplete`, `list_coin_duties`, `update_duty_description` all already call `.get()` and will benefit automatically.
- `delete_coin` is explicitly out of scope for this step (it doesn't raise `DoesNotExist` today - it silently no-ops on a missing coin_path; that's part of Step 2 below).
- Add tests:
  - `GET /api/coins/{nonexistent-path}` -> expect `404`
  - `GET /api/duties/{nonexistent-number}` -> expect `404`

### Step 2 - TODO
Add a global exception handler for `peewee.IntegrityError` -> `409 Conflict`, covering:
- Duplicate coin/duty creation (`add_coin`, `add_duty`).
- Replace the existing ad-hoc `try/except IntegrityError` in `delete_coin` (currently returns 200 with a string body) with the same 409 behavior.

### Step 3 - TODO
Fix `delete_coin` to return `404` when the coin doesn't exist, instead of silently reporting "Coin deleted" for zero rows affected. Fetch via `Coin.get(...)` first (letting `DoesNotExist` propagate to the Step 1 handler), then delete.

### Step 4 - TODO
Review `coins_ui.py` call sites (`edit_coin_page`, `create_coin_submit`, `delete_coin_submit`, etc.) that call `coins_api` functions directly, to decide whether raised `DoesNotExist`/`IntegrityError` should be caught there for a friendlier UI experience (redirect / flash message) rather than surfacing the generic JSON error response.

### Step 5 - TODO
Add remaining tests:
- DELETE `/api/coins/{nonexistent}` -> 404 (behavior change from current silent 200)
- POST `/api/coins` with duplicate `coin_name`/`coin_path` -> 409 (currently 500)
- POST `/api/duties` with duplicate `duty_number` -> 409 (currently 500)
- PUT `.../add-duties` and `.../remove-duties` with nonexistent coin_path or duty number -> 404
- DELETE `/api/coins/{path}` when it still has associated duties -> 409 (replaces old string-based check)

### Step 6 - TODO
Update `README.md` "Note on error handling and validation" section to remove the now-fixed known issues.
