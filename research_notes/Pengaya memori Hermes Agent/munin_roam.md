# Munin and Hermes Roam: memory add-ons for Hermes Agent (verified Nov 2026)

## Q1. What are the exact sources, and do they match the Instagram description?

### Takeaway
Both are real, third-party plugins listed in the official Hermes Agent marketplace. Both catalog PRs were merged by teknium1 (Nous) on Nov 8-9, 2026, and both repos were created on Nov 7, 2026. Munin (Munin Labs) is a thin MCP connector to a commercial, invite-only SaaS meeting app. Hermes Roam (Victor Cruz, vcruz305) is a self-hosted encrypted sync tool for `~/.hermes`. The carousel descriptions match the products' own docs closely. The "Munin" meeting app is not the Munin monitoring tool, and "Hermes Roam" is not Roam (ro.am).

### Cited Findings
- Munin marketplace listing: author `munin-labs`, repo https://github.com/Munin-Labs-AI/munin-hermes-plug-in, v0.1.0, requires Hermes Agent >= 0.23.0, category Tools, MIT license for the repo. The hosted service and MCP server fall under Munin's own terms. — [Hermes marketplace: munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- Munin catalog PR #150768 was opened Nov 7, 2026 by Hugo6991 on behalf of Munin-Labs-AI. teknium1 merged it Nov 8, 2026 (commit 41f884a) with 27 checks passing, labels `ci-reviewed`, `comp/plugins`, `tool/mcp`. No formal reviews were recorded. The author posted an 82-second demo video on Nov 10. — [PR #150768](https://github.com/NousResearch/hermes-agent/pull/150768)
- Hermes Roam marketplace listing: author Victor Cruz, repo https://github.com/vcruz305/hermes-roam, v0.5.6, Apache-2.0, install count shown as 1. — [Hermes marketplace: hermes-roam](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Hermes Roam catalog PR #150563 by vcruz305 was opened Nov 7, 2026 with 12 commits. teknium1 requested changes on Nov 8, then approved and merged on Nov 9, 2026, pinned to commit 8b9fba4 (v0.5.6). It is linked to feature request issue #20510 ("Cloud Sync for All Hermes Configurations Across Devices"). — [PR #150563](https://github.com/NousResearch/hermes-agent/pull/150563); [Issue #20510](https://github.com/NousResearch/hermes-agent/issues/20510)
- Munin product site: "agent native meeting app" by Munin Labs (© 2026 Munin Labs). — [muninlabs.ai](https://muninlabs.ai)
- Name collisions:
  - "Munin" is also a long-standing open-source network and system monitoring tool. It is unrelated. — [Wikipedia: Munin (software)](https://en.wikipedia.org/wiki/Munin_(software))
  - Product Hunt lists a "Munin/MuninX", an open-source headless HubSpot alternative by Kjell Rune Monsø. It is also unrelated. — [Product Hunt muninx](https://www.producthunt.com/products/muninx)
  - Roam (ro.am, a virtual-office/chat product) has its own Hermes integration that runs a Hermes bot inside Roam chat. It does no memory sync and is unrelated to hermes-roam. — [developer.ro.am Hermes integration](https://developer.ro.am/docs/integrations/hermes)
  - A different repo, rtsitola/hermes-roaming, does Hermes memory roaming via Syncthing with a master-slave design. It is unrelated to vcruz305/hermes-roam. — [rtsitola/hermes-roaming](https://github.com/rtsitola/hermes-roaming/tree/main)

### Inferences
- The carousel phrasing ("checked against the transcript down to the minute", "storage you own", "AES-256") echoes the marketplace and README text almost word for word. The promoter likely paraphrased the listings within days of the merges.
- Neither plugin was written or endorsed by Nous Research beyond the catalog review and merge. A catalog listing reviews the disclosure and pinned SHA. It is not an endorsement of the backend service.

### Gaps
- I could not find the julian.goldie_ Instagram carousel itself. His public "best Hermes plugins" blog pages do not mention Munin or Roam. — [aisuccesslabjuliangoldie.com](https://aisuccesslabjuliangoldie.com/blog/best-hermes-agent-plugins/)
- I did not find who Munin Labs is (founders, jurisdiction). The site gives no company location.

## Q2. Munin: what is it technically, is it open source, is it "free", and how does citation to a timestamp work?

### Takeaway
Munin is a commercial, cloud SaaS meeting recorder. A Mac menu-bar app and a web app record mic plus call audio with no bot, ElevenLabs transcribes in the cloud, and storage is Supabase in Tokyo. It is invite-only with no published pricing. The Hermes plugin is only an MIT-licensed manifest plus two skills that point Hermes at Munin's hosted MCP server (OAuth 2.1). "Citations to the minute" come from the server returning transcript lines with line ids and seconds. The LLM then compares the AI-written decisions against those lines by following skill instructions. Nothing about this check is cryptographic or deterministic.

### Cited Findings
- Recording: the Mac app records from the menu bar, capturing the mic and call audio, so it works with Zoom, Meet and Teams. No bot joins. A web recorder is also available. — [muninlabs.ai](https://muninlabs.ai)
- Transcription happens in the cloud via ElevenLabs, with speaker labels by name. — [muninlabs.ai](https://muninlabs.ai)
- Privacy: meetings are stored with Supabase in Tokyo. The service is not end-to-end encrypted and has no fully local mode. Agents get access only after the user allows it, and access can be revoked. No retention period is stated on the homepage. — [muninlabs.ai](https://muninlabs.ai)
- Access: invite-only, through a waitlist or an invite code from an existing user. No pricing appears on the site. — [muninlabs.ai](https://muninlabs.ai); the PR also says "Munin sign-up is invite-gated." — [PR #150768](https://github.com/NousResearch/hermes-agent/pull/150768)
- Hermes integration: a "portable plugin with no Python code" that uses the remote MCP server `https://app.muninlabs.ai/mcp` (Streamable HTTP), OAuth 2.1 with PKCE and dynamic client registration, and no API key. It requests scope `meetings:read`. Read-only or editable access is chosen on Munin's consent page. Tokens live in `~/.hermes/mcp-tokens/`. — [marketplace munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- MCP tools are exposed as `mcp__munin__<tool>`:
  - Read tools: `list_meetings`, `get_meeting` (notes, decisions with clock times, open questions, speakers), `search_transcripts`, `get_transcript` (by time range and page), `list_series`, `search`, `fetch`.
  - Write tools: `set_speaker` and `import_meeting`, which appear only with an editable connection.
  - Source: [marketplace munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- Skills:
  - `munin-followup` checks decisions against the transcript, moves unsupported items to a "needs confirmation" list, and drafts a follow-up message.
  - `munin-recall` covers who said what and when, and compares recurring meetings.
  - Source: [marketplace munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- Citation format is `meeting <id> · mm:ss · L<n>`. The check requires the server to return lines with speaker, line id and second, and decisions with their second. Hermes performs the comparison by following the skill's instructions. — [GitHub munin-hermes-plug-in README](https://github.com/Munin-Labs-AI/munin-hermes-plug-in)
- Munin itself writes the notes (verdict, summary, decisions with time said, open questions, chapters, quotes, speakers) from the transcript. — [GitHub README](https://github.com/Munin-Labs-AI/munin-hermes-plug-in)
- The README does not use the words "signed" or "unsigned". The demo line "decision entries are AI-summarized and unsigned" most likely comes from the agent's or server's output, not from the docs. — [GitHub README](https://github.com/Munin-Labs-AI/munin-hermes-plug-in)
- Safety and data flow:
  - Every tool call goes to app.muninlabs.ai over HTTPS. Meeting notes, transcript lines and names reach whatever LLM runs Hermes.
  - The plugin itself has no telemetry, no hooks, no local code and no self-update, and it never records audio.
  - The skills tell Hermes to treat transcript text as data and not follow instructions found inside meetings.
  - Source: [marketplace munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- Trust caveat: the plugin marks the server `untrusted`, so Hermes asks before write calls. However, the `hermes mcp add` entry needed for OAuth overrides that unless the user adds `trust: untrusted`. — [marketplace munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- Install:
  1. `hermes plugins install Munin-Labs-AI/munin-hermes-plug-in --no-enable`
  2. `hermes plugins enable munin`
  3. `hermes mcp add munin --url https://app.muninlabs.ai/mcp --auth oauth`
  4. `hermes mcp login munin`
  5. `hermes mcp test munin`
  - It requires a Munin account with at least one processed meeting. — [marketplace munin](https://hermes-agent.nousresearch.com/marketplace/munin)
- Verification in the PR:
  - `hermes plugins validate` passed on v0.23.0 and the security scan reported "safe".
  - The author's end-to-end test against the live server with a demo account listed 9 tools, returned cited answers, and the untrusted gate blocked a speaker rename.
  - Source: [PR #150768](https://github.com/NousResearch/hermes-agent/pull/150768)
- Maturity as of 2026-11-11:
  - GitHub API: 0 stars, 0 forks, 0 open issues, created 2026-11-07, last push 2026-11-07, MIT, language reported as Python. — [api.github.com](https://api.github.com/repos/Munin-Labs-AI/munin-hermes-plug-in)
  - Repo: 4 commits, no releases, no tests folder at the top level. Top-level folders are `.agents/skills/verify-munin-hermes`, `assets`, `catalog`, `scripts`, `skills`. — [GitHub](https://github.com/Munin-Labs-AI/munin-hermes-plug-in)
- Pricing search turned up nothing from muninlabs.ai. — WebSearch "Munin Labs muninlabs.ai pricing agent native meeting app" (no relevant results)

### Inferences
- "Open source" applies only to the thin connector (manifest plus skill prompts). The recorder, transcription, summarization and MCP server are closed and commercial.
- I found no evidence for a "free" claim. The only "free" part is the MIT connector. The service has no published price and is invite-gated, so a free tier is unconfirmed. Treat a "free" framing as inaccurate or unverified.
- Privacy risk is significant. Audio and transcripts go to a cloud SaaS (ElevenLabs for STT, Supabase in Tokyo for storage, not E2E), and transcript contents also flow to the user's LLM provider. Transcripts are also a prompt-injection surface, which the skills mitigate only through instructions.
- "Checked down to the minute" is LLM-driven cross-referencing of server-supplied timestamps. It is useful grounding, but it is not a guarantee. A hallucinated citation would only be caught if the model actually calls `get_transcript` and compares.
- The repo reports Python as its language despite the "no Python" claim. This probably comes from helper scripts in `scripts/` or `.agents/` used for verification and not shipped as plugin code. Not verified.

### Gaps
- Pricing, the free tier, the retention period and the full privacy policy were not found. I did not fetch the privacy policy page.
- The internals of the MCP server (how decisions get their "second" timestamps, and which LLM summarizes them) are undisclosed.
- Who Munin Labs is, and where it is incorporated.

## Q3. Hermes Roam: what does it sync, how does the crypto work, and how does it handle conflicts?

### Takeaway
Hermes Roam is a self-hosted, open-source (Apache-2.0) Python plugin. It zips a selected subset of `~/.hermes` and seals each push as one AES-256-GCM envelope. The 32-byte `ROAM_ARCHIVE_KEY` is user-generated and copied manually to each device. The remote head is signed with HMAC-SHA256 using an HKDF-derived key. Storage backends are S3/R2, a private git repo, or a local directory. Conflict handling is single-writer compare-and-swap with no content merge. A file edited on both sides is flagged as a conflict and kept local. The plugin is very new (2 stars, 17 commits, created Nov 7, 2026), but it has a large claimed test suite and passed a real maintainer review.

### Cited Findings
- What syncs:
  - Always: `skills/`, `memories/`, `SOUL.md`, `skins/`, `hermes-pack.yaml`, `profile.yaml`, and `config.yaml` (host-specific keys are stripped on push and kept local on pull).
  - `roam/installed-plugins.json`, which holds plugin names and SHAs. Plugin code is never synced; other devices reinstall from source.
  - `profiles/<name>/` trees, and a device can exclude a profile.
  - Source: [marketplace hermes-roam](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Opt-in, off by default:
  - A session archive (`sync_sessions`): redacted, read-only markdown exports capped at 50 MB, with best-effort redaction.
  - Cron definitions (`sync_cron`): pulled jobs land paused.
  - Hooks, enabled through a `shared:` rule in `roam/rules.yaml`.
  - Source: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Never synced: `.env`, `auth.json`, `state.db`, raw `sessions/`, caches and logs, unmodified bundled skills, hub-installed skills, plugin code, and `<home>/roam/`. — [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam). The PR adds that secret-like keys in `config.yaml` are not synced either. — [PR #150563](https://github.com/NousResearch/hermes-agent/pull/150563)
- Crypto:
  - Each bundle is a zip sealed as one AES-256-GCM envelope with a 12-byte random nonce.
  - A canonical-JSON header (version, device, generation, digests) is authenticated as AAD.
  - The remote HEAD is signed with HMAC-SHA256, using a key derived from the archive key via HKDF so it is distinct from the bundle key.
  - A wrong key fails authentication before anything is extracted.
  - Source: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Keys:
  - `ROAM_ARCHIVE_KEY` is 32 bytes (base64 or 64 hex characters) and must be the same on every device.
  - The setup skill generates it with Python `secrets` and tells the user to put it in `{home}/.env` themselves, not to paste it in chat.
  - S3 credentials (`ROAM_S3_ACCESS_KEY_ID` and `ROAM_S3_SECRET_ACCESS_KEY`) come only through Hermes's secret scope.
  - Source: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- The README does not publish the HKDF info strings or salt, and it has no dedicated threat-model section. The closest is a "How it is safe" section. — [GitHub hermes-roam](https://github.com/vcruz305/hermes-roam)
- Backends:
  - `s3` (boto3; works with Cloudflare R2 using region `auto`, and a live R2 run is documented).
  - `git` (git CLI with existing SSH or credential helper; keep the shared home under about 50 MB).
  - `local` (tests and demos only, POSIX-only because it uses `flock`).
  - Dropbox and rclone are not mentioned.
  - Source: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Conflicts:
  - Head updates use compare-and-swap. S3 rejects stale writes with HTTP 412, and git uses `--force-with-lease`.
  - If the remote is ahead, `push` exits with code 2 and asks for a pull first.
  - Config files are compared against the last accepted version. A change on both sides counts as a conflict and stays local unless `--overwrite-conflicts` is passed.
  - A rollback floor blocks a remote being served at a lower generation.
  - Source: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- The README says "There is no three-way merge of file contents", supports one writer at a time, and does not do content merging. `memories/` follows the same file-level rules. MEMORY.md and USER.md get no special handling. — [GitHub hermes-roam](https://github.com/vcruz305/hermes-roam)
- Apply safety:
  - `pull` shows a plan only. `pull --apply` installs through a journal with backups and rolls back on failure.
  - `history` and `restore` recover earlier generations.
  - The agent tools `roam_status`, `roam_push` and `roam_pull` refuse apply unless `allow_agent_apply` is set (default false).
  - Remote-controlled text is quoted and length-capped before it reaches the model.
  - Sources: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam); [PR #150563](https://github.com/NousResearch/hermes-agent/pull/150563)
- Auto sync is optional through the `on_session_start`, `on_session_end` and `pre_llm_call` hooks, which are off by default. Session start pulls only `skills/`, `memories/` and `SOUL.md`, never `config.yaml`. Session end runs a debounced push only when shared files changed. — [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Install:
  - `hermes plugins install hermes-roam` (or `vcruz305/hermes-roam`), then `hermes plugins enable hermes-roam`.
  - The bundled `roam-setup` skill walks through setup.
  - Requirements: Hermes >= 0.22.0, Python 3.11+, `cryptography`, `pyyaml`, `boto3`.
  - Source: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam)
- Limitations:
  - Secrets must be set up per device.
  - `config.yaml` comments are lost on merge because of PyYAML.
  - There is no Desktop UI.
  - The local backend is POSIX-only.
  - Source: [GitHub](https://github.com/vcruz305/hermes-roam)
- Review history:
  - teknium1 requested changes on Nov 8. Pulled cron jobs would run immediately and were written outside the cron lock, and git received the full `os.environ`.
  - The author fixed these in 0.5.3: jobs land paused and are written under the lock, and git gets an allowlisted environment.
  - 0.5.4 and 0.5.5 fixed Windows file handling. 0.5.6 fixed a secret-scope bug under Hermes 0.23 that had silently broken auto-sync.
  - Approved Nov 9.
  - The author claims 613 tests on Python 3.11 and 3.14, two adversarial review rounds, a live R2 run, and a live Linux-to-Windows 11 run.
  - Source: [PR #150563](https://github.com/NousResearch/hermes-agent/pull/150563)
- Maturity as of 2026-11-11:
  - GitHub API: 2 stars, 1 fork, 0 open issues, created 2026-11-07, last push 2026-11-08, Apache-2.0, Python. — [api.github.com](https://api.github.com/repos/vcruz305/hermes-roam)
  - Repo: 17 commits, no GitHub releases, a `tests/` directory present. The README says 586 tests and ruff clean, which conflicts slightly with the PR's 613. — [GitHub](https://github.com/vcruz305/hermes-roam)

### Inferences
- The "AES-256" claim is accurate and specific: AES-256-GCM with AAD and an HMAC-signed head. The design is sound on paper: authenticated encryption, rollback protection, CAS. It has not been independently audited, and the HKDF parameters are not documented in the README.
- Key distribution is manual, with no passphrase KDF. Losing `ROAM_ARCHIVE_KEY` means losing the history. Anyone holding the key plus bucket access can read everything.
- Memory merge is a real limitation for agent memory. If two machines both append to a memory file between syncs, one side's change is held as a local conflict, and resolving it is manual or means overwriting. There is no CRDT or line merge.
- The 586 vs 613 test count probably reflects the README lagging behind the latest version. Neither number was verified by running the suite.
- The rapid patch cadence (0.5.3 to 0.5.6 within about two days, including a bug that silently broke auto-sync) shows active fixing but also signals early-alpha stability.

### Gaps
- HKDF salt and info strings, nonce-reuse analysis, and key rotation procedure were not found.
- Whether a GitHub Actions CI workflow exists and passes was not visible.
- I found no independent security review or user reports (Reddit/X) for either plugin.

## Q4. How do they integrate into Hermes Agent?

### Takeaway
Both are marketplace "plugins" installed with `hermes plugins install` and arriving disabled. Munin is a portable plugin that registers a remote MCP server plus two skills, with no local code. Hermes Roam is a Python plugin that adds a `hermes roam` CLI subcommand and slash command, three agent tools, optional session hooks, and a setup skill.

### Cited Findings
- Munin consists of a plugin manifest (`plugin.json`, `mcp.json`) plus skills. Tools surface as `mcp__munin__*` through Hermes's MCP client, and the OAuth config lives under `mcp_servers` in `~/.hermes/config.yaml`. — [GitHub](https://github.com/Munin-Labs-AI/munin-hermes-plug-in); [marketplace](https://hermes-agent.nousresearch.com/marketplace/munin)
- Hermes Roam adds:
  - CLI commands: `hermes roam push`, `pull`, `history`, `restore`, `auto`.
  - Tools: `roam_status`, `roam_push`, `roam_pull`.
  - Hooks: `on_session_start`, `on_session_end`, `pre_llm_call`.
  - Skill: `roam-setup`.
  - Desktop deep link: `hermes://plugin/install?catalog=hermes-roam`.
  - Sources: [marketplace](https://hermes-agent.nousresearch.com/marketplace/hermes-roam); [PR #150563](https://github.com/NousResearch/hermes-agent/pull/150563)
- Hermes discovers user plugins from `~/.hermes/plugins/<name>/`. — [developer.ro.am](https://developer.ro.am/docs/integrations/hermes)

### Inferences
- Red flags summary:
  - Munin: a commercial, invite-only cloud service behind an MIT wrapper. No public pricing. Data leaves the machine to ElevenLabs and Supabase (Tokyo), with no E2E. The OAuth config can silently drop the `untrusted` write gate. 0 stars and 4 commits.
  - Hermes Roam: a single maintainer, a 4-day-old repo, a manual key, no content merge, no audit.
  - Both appeared in an influencer post within days of their catalog merges.

### Gaps
- Searches run with no relevant extra results: "julian goldie Hermes agent Munin Roam plugins" and "Munin Labs muninlabs.ai pricing agent native meeting app". No Reddit or X discussion was found.
