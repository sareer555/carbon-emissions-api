# SMB Carbon Emissions Calculator API

A REST API that lets small and medium businesses estimate their Scope 1
(direct fuel) and Scope 2 (purchased electricity) carbon emissions using
standard, publicly published emission factors — without a $50K/year ESG
platform or a sustainability consultant.

Built as an "emissions calculation engine as a service": other apps
(accounting software, ESG reporting tools, marketplaces wanting a carbon
badge) embed it via API instead of building the calculation logic
themselves.

**Scope 3 (supply chain) emissions are explicitly out of scope for v1** —
save for a later paid tier.

---

## Emission factor provenance

Every response carries a `disclaimer` field and cites the exact factor
source + year used, per the project's non-negotiable trust requirements.

The seed data in [`app/seed/factors_data.py`](app/seed/factors_data.py)
was verified on 2026-08-21 directly against the primary spreadsheets:

- **US Scope 1 fuels**: EPA "GHG Emission Factors Hub" (2025 edition),
  Table 1 — Stationary Combustion.
- **US Scope 2 grid**: EPA eGRID Summary Tables 2023 (eGRID2023 data),
  Table 1 — Subregion Output Emission Rates. All 27 eGRID subregions plus
  a `US-AVG` national average are included.
- **UK Scope 2 grid**: UK Government (DEFRA/DESNZ) GHG Conversion Factors
  for Company Reporting, 2026 full set, "UK electricity" tab.

CO2 + CH4 + N2O are combined into CO2e using the IPCC AR5 100-year GWPs
(CH4 = 28, N2O = 265) cited in the EPA Hub itself, applied consistently
across every row. Each row's `notes` field shows the exact arithmetic from
the source spreadsheet to the stored factor, so every number is
re-derivable and auditable.

Emission factors are republished annually (EPA Hub/eGRID yearly; DEFRA
every June) — re-verify against the current primary spreadsheets on that
cadence. See "Refreshing emission factors" below.

Never use "certified," "verified" (as a claim about the *emissions*
themselves), or "compliant" anywhere in the product — only "estimated" /
"calculated using [source]."

---

## Quickstart (local, $0 cost)

```bash
cd carbon-emissions-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env          # defaults to a local SQLite file, no DB setup needed

python -m app.seed.seed_db                              # load emission factors
python -m app.scripts.create_api_key --plan free --label "my-test-key"  # save the printed key!

uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for interactive Swagger docs, or:

```bash
curl http://127.0.0.1:8000/v1/health

curl -X POST http://127.0.0.1:8000/v1/calculate/scope1 \
  -H "Authorization: Bearer <your key>" -H "Content-Type: application/json" \
  -d '{"fuel_type": "natural_gas", "quantity": 500, "unit": "therms"}'
```

Run the test suite:

```bash
python -m pytest
```

---

## API

Base path: `/v1`. Auth: `Authorization: Bearer <api_key>` on every route
except `/v1/health`.

| Endpoint | Auth | Description |
|---|---|---|
| `GET /v1/health` | none | Uptime check |
| `GET /v1/factors` | required | List all supported fuel types + grid regions, with current factors/sources |
| `POST /v1/calculate/scope1` | required | Direct fuel combustion emissions |
| `POST /v1/calculate/scope2` | required | Purchased electricity emissions |
| `POST /v1/calculate/batch` | required | Sum many Scope 1 + Scope 2 line items in one call (e.g. a year of utility bills) |
| `POST /v1/admin/keys` | admin token | Issue a new customer API key. Only for provisioning keys where shell access isn't available (e.g. Render free tier) — see "Deploying at $0 cost" below. Disabled (404) unless `ADMIN_BOOTSTRAP_TOKEN` is set. |

Full interactive spec: `/docs` (Swagger UI) and `/openapi.json`.

### Supported fuel types (Scope 1)

`natural_gas` (therms, mmBtu, ccf), `diesel` (gallons, liters), `gasoline`
(gallons, liters), `propane` (gallons, liters). See `GET /v1/factors` for
the live list and units accepted per fuel — conversions are handled
server-side (`app/services/units.py`).

### Supported grid regions (Scope 2)

All 27 EPA eGRID subregions (`US-CAMX`, `US-ERCT`, `US-NYUP`, `US-RFCW`,
`US-FRCC`, `US-MROW`, etc. — see `GET /v1/factors` for the full list),
plus a `US-AVG` national-average fallback for callers who don't know their
customer's subregion.

Every region is year-keyed, since both EPA eGRID and UK DEFRA republish
new factors annually and a customer reconciling last year's utility bills
should get last year's factor, not this year's: `US-CAMX-2023`, `US-AVG-2023`,
`UK-2025`, `UK-2026`, etc. hold each dataset's explicit reporting-year
factor, and the bare key (`US-CAMX`, `US-AVG`, `UK`) is a convenience
alias that always tracks the latest dataset verified in
`app/seed/factors_data.py`. Expand to other countries or add a new year by
adding rows — see the roadmap in the
original build brief for a request-driven expansion plan.

### Error shape

```json
{"error": {"code": "INVALID_FUEL_TYPE", "message": "..."}}
```

Codes: `UNAUTHORIZED`, `MONTHLY_QUOTA_EXCEEDED`, `RATE_LIMITED`,
`INVALID_FUEL_TYPE`, `INVALID_REGION`, `INVALID_UNIT`, `INVALID_REQUEST`,
`VALIDATION_ERROR`, `NOT_FOUND`, `INTERNAL_ERROR`.

---

## Architecture

```
app/
  main.py              FastAPI app, routers, CORS, exception handlers
  config.py             Settings (pydantic-settings, reads .env)
  database.py            SQLAlchemy engine/session (SQLite dev / Postgres prod)
  models.py               emission_factors / api_keys / request_log tables
  schemas.py               Pydantic request/response models
  errors.py                 Typed exceptions -> consistent {"error": {...}} shape
  auth.py                    Bearer API-key auth + monthly quota enforcement
  rate_limit.py               Per-key burst limiter (in-memory, or Redis if REDIS_URL is set)
  logging_config.py            Writes one request_log row per calculation call
  routers/{health,factors,calculate,admin}.py
  services/{emissions,units}.py   Calculation engine + unit conversion
  seed/{factors_data,seed_db}.py   Emission factor seed data + loader script
  scripts/create_api_key.py         Issue a new API key (prints plaintext once)
```

Database schema matches the build brief (`emission_factors`, `api_keys`,
`request_log`) — see `app/models.py`.

---

## Deploying at $0 cost

### Fastest path: Render Blueprint (one click)

This repo includes [`render.yaml`](render.yaml) — a Render Blueprint that
provisions the web service **and** a free Postgres database together, wires
`DATABASE_URL` between them automatically, and seeds the emission factors
on first deploy.

1. Go to [render.com](https://render.com), sign in with GitHub.
2. **New +** → **Blueprint** → select `sareer555/carbon-emissions-api`.
3. Render reads `render.yaml` and provisions everything. First deploy takes
   a few minutes.
4. Render's free tier has **no Shell access**, so issue your first API key
   over HTTP instead of via `create_api_key.py`:
   - In the web service's **Environment** tab, find the auto-generated
     `ADMIN_BOOTSTRAP_TOKEN` value (click to reveal it).
   - Open `/docs`, expand `POST /v1/admin/keys`, click **Authorize** and
     paste that token as the bearer token, then **Try it out** with a body
     like `{"plan": "free", "label": "first-key"}`.
   - Copy the `api_key` from the response immediately — it's shown once,
     never stored in plaintext. This endpoint 404s for anyone without the
     token, and 401s on a wrong one (see `app/routers/admin.py`).
5. Your API is now live at `https://<your-service-name>.onrender.com`. Try
   `GET /v1/health` and `/docs`.

Render's free web service tier spins down after inactivity and takes ~30s
to wake on the next request — fine for evaluation/early customers, upgrade
the plan once you have paying traffic that can't tolerate the cold start.

### Other free-tier options

| Layer | Free option |
|---|---|
| Hosting | Render or Fly.io free tier — `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Database | Render, Supabase, or Neon Postgres free tier — set `DATABASE_URL` |
| Rate limiting across instances | Upstash Redis free tier — set `REDIS_URL` |
| Docs | Free — FastAPI auto-generates `/docs` and `/openapi.json` |
| Distribution | List the OpenAPI spec on RapidAPI (handles billing/discovery); self-host + Stripe for direct customers later |

For local Postgres instead of SQLite: `docker compose up` (spins up the API
+ a Postgres container and seeds it automatically).

Docker image (seeds on build against a local SQLite file; point
`DATABASE_URL` at Postgres and re-run `python -m app.seed.seed_db` in prod):

```bash
docker build -t carbon-emissions-api .
docker run -p 8000:8000 -e DATABASE_URL=<your-postgres-url> carbon-emissions-api
```

---

## Refreshing emission factors

Grid regions (Scope 2) follow an **explicit-year + alias** pattern — see
"Supported grid regions" above. When a new year's dataset is published:

1. Download the current source spreadsheet: [EPA GHG Emission Factors Hub](https://www.epa.gov/climateleadership/ghg-emission-factors-hub), [EPA eGRID](https://www.epa.gov/egrid), [UK DEFRA/DESNZ conversion factors](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting).
2. **Add** new `-YYYY` rows to `app/seed/factors_data.py` for the new year — don't overwrite the prior year's row. Include `source_year` and a `notes` entry showing the source-to-factor arithmetic (see the existing rows for the format).
3. **Repoint the bare-key alias** (e.g. `US-CAMX`, `UK`) to the new year's value once it's verified, so integrators who didn't pin a year automatically move forward.
4. Run `python -m app.seed.seed_db` — it upserts by `(category, key)`, so existing rows are updated in place and history isn't lost from `request_log`.
5. Never delete a prior year's `-YYYY` row a customer might be reconciling historical activity against, and never delete a factor a customer might have already been billed against without checking `request_log` first.

---

## Business model (for context, not enforced by the code)

- Free: 100 calls/month · Starter: $9/mo (1,000) · Growth: $29/mo (10,000) · Scale: $79/mo (100,000)
- Quotas are enforced per plan in `app/config.py` (`plan_quotas`) and checked on every authenticated request.
- Target: $50–100 MRR from 5–15 paying developers before reinvesting in infra.
