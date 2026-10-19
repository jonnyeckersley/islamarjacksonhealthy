# Is Lamar Jackson Healthy?

A static, mobile-friendly fan site for GitHub Pages. No backend or paid hosting required.

## Publish on GitHub Pages
1. Create a public GitHub repository (e.g. `islamarjacksonhealthy`).
2. Upload the contents of this folder, **including the CNAME file**, to the repository root.
3. Go to **Settings → Pages**. Choose **Deploy from a branch**, branch **main**, folder **/(root)**, then Save.
4. In GoDaddy DNS, create four A records for host `@` pointing to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`. Remove conflicting A records for `@`. Add CNAME `www` → `YOUR-GITHUB-USERNAME.github.io` (replace username). Keep unrelated MX/TXT email records intact.
5. In GitHub Settings → Pages, set custom domain `islamarjacksonhealthy.com` and enable **Enforce HTTPS** after certificate issuance.

## Injury report data (important)
The site is intentionally **UNKNOWN by default**. A verified automatic injury-report parser is **not included**: the official Ravens report has not yet been validated for reliable, permitted automated extraction. The hourly GitHub workflow only checks freshness; it does NOT fetch injury reports. Do not advertise this version as automatically tracking injury status.

To publish a verified update, edit `status.json`:
```json
{"status":"no","reason":"Lamar Jackson was limited in practice (ankle).","updated_at":"2026-10-19T17:00:00Z","source_url":"https://www.baltimoreravens.com/team/injury-report/"}
```
Use `yes` only with a verified current report showing full participation or no reported restrictions; `no` for limited/non-participation or a questionable/doubtful/out game designation; `unknown` for missing or ambiguous data. **Never infer medical health** from these labels. The page automatically falls back to UNKNOWN after 48 hours. Practice reports may not be published daily, so the freshness threshold is conservative.

## Countdown
The client fetches upcoming Ravens games from ESPN's public schedule endpoint. This is an unofficial endpoint and could change or restrict cross-origin access. If unavailable, the site links to the official Ravens schedule rather than displaying an invented kickoff.

## Notes
No official Ravens/NFL marks or logos are bundled. The site is clearly labeled as unofficial.
