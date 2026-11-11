# Hermes Agent memory add-ons: hermes-dreaming and jai-srinivas/mindhall (as of 2026-11-11)

Scope note: the Instagram carousel by julian.goldie_ itself was not retrieved. The claims checked below are the ones relayed in the assignment. Both repos were found and inspected directly (README, API metadata, and for mindhall the source files).

## 1. Do the repos exist, and do they match the carousel? Exact URLs and authors

### Takeaway
Both exist. "hermes-dreaming" is **github.com/itpartypattaya/hermes-dreaming** by Anton Vaskov. It has 23 stars, which matches the carousel's "~23". Beware a name collision with a different PyPI package of the same name. "mindhall" is **github.com/jai-srinivas/mindhall**. It was created 2026-11-07 and has 0 stars, 0 forks and one human author, which matches the carousel.

### Cited Findings
- hermes-dreaming: full_name `itpartypattaya/hermes-dreaming`. Description: "Nightly deterministic memory consolidation ("dreaming") skill for Hermes Agent". Created 2026-08-16, last push 2026-11-07. 23 stars, 3 forks, 1 open issue/PR. MIT license, Python. Topics: agent-memory, hermes-agent, llm-memory, memory-consolidation. — [GitHub API](https://api.github.com/repos/itpartypattaya/hermes-dreaming)
- The official Hermes docs catalog lists hermes-dreaming v3.8.6 as a **Community** plugin in the Memory category. The author is Anton Vaskov (GitHub itpartypattaya). The docs say it is not an official Nous Research product. — [Hermes docs: hermes-dreaming](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- Name collision: a separate project, **alejandroiglesias/hermes-dreaming**, is published on PyPI (v0.3.2). It uses a "Light → Deep → REM" cycle that compacts MEMORY.md and writes `~/.hermes/dreaming/DREAMS.md`. It is not the same code as the itpartypattaya plugin. — [PyPI hermes-dreaming](https://pypi.org/project/hermes-dreaming/); [project page](https://alejandroiglesias.github.io/hermes-dreaming/). I found these through search snippets only and did not inspect them in depth.
- Other similarly named items exist, such as Da7-Tech/dream, a generic text-based tool with no LLM calls, and a "Hermes Dream Memory Consolidation" skill on mcpmarket. — [search results: github.com/Da7-Tech/dream](https://github.com/Da7-Tech/dream), [mcpmarket](https://mcpmarket.com/tools/skills/hermes-dream-memory-consolidation)
- The hermes-atlas directory also lists itpartypattaya/hermes-dreaming. — [hermesatlas.com](https://hermesatlas.com/projects/itpartypattaya/hermes-dreaming)
- mindhall: `jai-srinivas/mindhall`. Description: "One shared mind for every AI you use". Created 2026-11-07T08:56Z, last push 2026-11-10. 0 stars, 0 forks, 0 open issues. MIT license, Python, no topics. — [GitHub API](https://api.github.com/repos/jai-srinivas/mindhall)
- mindhall commit authors are "Jai Srinivas" and "Varunsrini-bit", both with the same email address, so one person uses two identities. — [GitHub API commits](https://api.github.com/repos/jai-srinivas/mindhall/commits?per_page=100)
- A web search for "mindhall jai-srinivas" returned nothing relevant. The repo is not indexed or discussed anywhere I could find. — (WebSearch, 2026-11-11)

### Inferences
- The carousel's descriptions of both projects match the repos' own README taglines almost word for word. That suggests the carousel was built from the READMEs, not from hands-on testing.
- mindhall was about 4 days old when promoted. It had no external traction.

### Gaps
- I could not retrieve the Instagram carousel or check the exact posting date. I found no Reddit, X or HN discussion of mindhall. I did not search specifically for Reddit or HN threads about hermes-dreaming.

## 2. hermes-dreaming: how does "keeps facts backed by what people said" work, and what gets dropped?

### Takeaway
The nightly pass is a deterministic Python script that uses only the standard library. It scores candidate facts from recent chats with OpenClaw-style weights. A fact passes a **corroboration gate** only when *humans* said it on *distinct days* in *trusted* chats. The agent then applies at most a few changes through the normal Hermes `memory` tool. An optional LLM "judge" can only veto evidence, never add it. Secrets and injection text are quarantined, dated events expire, and rejected facts go on a reject list. Stale entries are not deleted silently. The agent asks about them first.

### Cited Findings
- Pipeline: the nightly `dream.py` is deterministic, makes no LLM calls by default, and never writes memory itself. A wake gate (`dream-precheck.py`) prints `{"wakeAgent": false}` on quiet nights, so the model is never started. On other nights the agent applies proposals through the `memory` tool, capped at 6 changes a night with at most 3 new entries. An extraction job (`dream-extract-precheck.py`) adds candidate facts through `fact_store`. A `no_agent` forget sweep runs every 15 minutes. — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming)
- Corroboration rule: "A fact counts only when humans mention it on distinct days." Cron prompts, compaction banners, URLs, untrusted chats and the agent's own threads do not count. — [Hermes docs page](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- `trusted_chat_ids` is fail-closed. If it is empty, no group chat corroborates memory. `trust_private_chats` defaults to true. — [Hermes docs page](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- Scoring uses OpenClaw-style weights (relevance, frequency, diversity, recency, consolidation, richness) with the corroboration gate on top. Matching against existing memory has three layers: exact, declarative alias rules, and stemmed containment. It uses character n-grams for CJK and Thai and diacritic-free stems for Latin scripts. A repeated fact with different numbers is flagged as a `conflicts` update, not treated as a duplicate. — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming)
- Provenance: each candidate carries an origin of said, confirmed or inferred. A fact repeated on two or more days gains trust (+0.05, at most 10 facts a night; requires holographic ≥ 0.15.0). With holographic ≥ 0.19.0, duplicates produce at most one "merge?" question per night, and a merge happens only after a human says yes. — [Hermes docs page](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- What is dropped or withheld:
  - Secrets and prompt injections are quarantined by a regex screen, which the README calls "not a guarantee".
  - Dated events expire.
  - Rejected facts go to a reject list and come back as a question only if people say them again after 180 days.
  - Stale entries are asked about, and an entry that survives rests for 90 days.
  - Forget sweeps remove forgotten facts from the plugin's own cache, judge files, diary and logs. They do not touch Git history, backups or Hermes session history.
  - A loss guard alerts when a large share of memory disappears overnight.

  — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming); [Hermes docs](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- Optional judge (off by default; modes `shadow` and `veto`): it asks a model whether each (fact, message) pair confirms, contradicts or is unrelated. It vetoes a pair when the answer is not "confirms" and confidence is at least tau (default 0.50). It can only remove counted pairs. Providers are OpenRouter `typesafe/jev-1.14` first, then OpenAI `gpt-6-luna` as fallback. Nightly limits are 250 calls, $0.05 (a soft cap) and 120 s. — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming); [Hermes docs](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- LLM exposure even without the judge: the nightly and extraction *agent* jobs send recent human messages (up to 200 messages or 40k characters) plus fact snippets to the configured Hermes model. — [Hermes docs](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- Judge accuracy claims are the author's own:
  - 84% (Jev) and 75% (OpenAI) of false confirmations removed on a 360-pair holdout, with 0 of 101 true confirmations removed.
  - Precision of counted pairs rose from 0.37 to 0.79 (Jev) or 0.71 (OpenAI).

  The README admits the holdout "was written by a model and not checked by a person". — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming)
- Storage:
  - Config: `~/.hermes/dreaming.json`, with keys `timezone`, `trusted_chat_ids`, `excluded_threads`, `untrusted_sources`, `fact_source` (holographic/sqlite/jsonl/none), `judge` and `chat_stores`.
  - State: `~/.hermes/cache/dream*.json`, mode 0600.
  - Diary: `~/.hermes/memories/DREAMS.md`, archived after 90 nights.
  - Supporting file: `cron-prompt-history.json`, a SHA256 allowlist of the shipped prompt templates.

  — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming)

### Inferences
- "Keeps facts backed by what people said" is a frequency and distinct-day corroboration heuristic over chat logs. It is not quote-level evidence linking or entailment checking unless the optional cloud judge is turned on. Even then, the judge only prunes evidence.
- The design is conservative: small caps, human confirmation for merges, fail-closed trust, and an approval queue. The trade-off is slow memory growth.

### Gaps
- I did not read `dream.py` itself, so the exact scoring weights and thresholds come from the README, not the code.
- I did not inspect the content of the one open issue or PR.

## 3. mindhall: how does the "signed change log" work, and how do ChatGPT and Claude connect?

### Takeaway
"Signed" is **not cryptographic**. Every write inserts a row into a SQLite `changes` table with a free-text `by` name and JSON before/after snapshots. There is no HMAC, signature, key or hash chain. Other AIs connect over **MCP** (streamable HTTP) to a self-hosted server. Authentication is only a secret embedded in the URL path. The signer name for MCP clients comes from the client's own self-declared `clientInfo.name`. There is no browser extension and no separate REST API for AIs, though the web UI has its own JSON API. Mindhall itself makes no LLM calls.

### Cited Findings
- Storage: a single local SQLite file at `~/.mindhall/mindhall.db`, overridable with `MINDHALL_DB`. `~/.mindhall/sessions.json` maps sessions to Hermes profiles. Text fields are capped at 500 characters. — [README](https://github.com/jai-srinivas/mindhall)
- Schema (`engine.py`): tables `about(id, note, updated_at)`, `work(id, name UNIQUE NOCASE, status DEFAULT 'Active', next_step, updated_at)`, `dates(id, day, what, work, updated_at)` and `changes(id, at, by, room, summary, before, after)`. The database uses WAL mode with a 5 s busy timeout. — [engine.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/engine.py)
- The log write is a plain insert: `INSERT INTO changes (at, by, room, summary, before, after)`, with `by or "Unknown"`. Before and after values are stored as `json.dumps`. The file imports only sqlite3, json, os, datetime and pathlib, with no crypto library. The write and its log entry share one transaction, which makes them atomic but not tamper-evident. — [engine.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/engine.py)
- Undo: `Mind.undo(change_id, by)` restores the `before` snapshot only if the row still equals the `after` snapshot. Otherwise it refuses with "This was changed again later. Undo the newer change first." The undo is logged as a new change. — [engine.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/engine.py)
- The README describes four "rooms": About you, Work, Dates and Change Log. Signers are the agent name (`MINDHALL_AGENT_NAME`), the connecting app (for example ChatGPT or Claude), or "You" for web edits. — [README](https://github.com/jai-srinivas/mindhall)
- MCP server (`mcp_server.py`):
  - Uses the official `mcp` Python SDK `MCPServer` class with Starlette, over the `streamable-http` transport.
  - The endpoint is `/{secret}/mcp`. `MINDHALL_MCP_SECRET` must be at least 24 characters, and requests without it get a 404.
  - Host and Origin checks are optional, enabled through `MINDHALL_MCP_ALLOWED_HOSTS`.
  - Default bind is 127.0.0.1:8765. The README says to expose it over HTTPS through a tunnel or your own domain, and that ChatGPT, Claude and Cursor add it as a custom connector.

  — [mcp_server.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/mcp_server.py); [README](https://github.com/jai-srinivas/mindhall)
- Signer identity for MCP clients: `app_name(ctx)` reads `ctx.session.client_params.client_info.name`, which the client declares itself. It maps substrings to display names ("claude-code" becomes "Claude Code"; "chatgpt" or "openai" become "ChatGPT"). Otherwise it uses the raw name or "AI app". `MINDHALL_MCP_AGENT_NAME` overrides it. — [mcp_server.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/mcp_server.py)
- Web UI routes are all under `/{secret}`: `/api/mind`, `POST/PATCH/DELETE /api/{kind}` and `POST /api/undo/{id}`, with `Cache-Control: no-store` and `Referrer-Policy: no-referrer`. — [mcp_server.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/mcp_server.py)
- Known issues, per the README:
  - Desktop-app sessions may sign under the default profile's name.
  - The MCP server relies on a secret URL instead of login. OAuth is planned.
  - A hosted version and a "memory-provider mode" are also planned.

  — [README](https://github.com/jai-srinivas/mindhall)

### Inferences
- The "signed change log" is an attribution and audit log, not a verifiable one. Any MCP client can claim any name, and anyone with database access can edit history. Calling it "signed" in marketing is misleading.
- Security model: anyone holding the URL has full read and write access to the user's shared memory. Exposing it publicly through a tunnel is risky until the planned OAuth exists.

### Gaps
- I did not read `settings.py` or `web/index.html`. I did not read the wiki guide linked from the README.

## 4. How do they hook into Hermes Agent's memory system? (with Hermes built-in memory context)

### Takeaway
Neither project is a Hermes memory provider. hermes-dreaming is an Agent Plugins v1 *skill plus cron jobs* that registers no tools or hooks and writes through Hermes's own `memory`, `fact_store` and `fact_feedback` tools. mindhall is a general Hermes plugin. It uses `pre_llm_call` context injection, a system-prompt section and 5 tools, and explicitly says it is "not a memory provider", so it can run alongside Honcho or Mem0.

### Cited Findings
- Hermes built-in memory, part 1: two files in `~/.hermes/memories/`. `MEMORY.md` (agent notes) is capped at 2,200 chars, about 800 tokens. `USER.md` (user profile) is capped at 1,375 chars, about 500 tokens. Both are loaded into the system prompt as a frozen snapshot at session start. Memory does not auto-compact: a write over the limit returns an error, and the agent must consolidate. The `memory` tool supports `add`, `patch` and `remove` with target `memory` or `user`. Entries are scanned for injection, exfiltration patterns and invisible Unicode. — [Hermes docs: Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- Hermes built-in memory, part 2:
  - All sessions are stored in SQLite at `~/.hermes/state.db` with FTS5 session search.
  - `memory.write_approval` (default false) stages non-foreground writes for `/memory pending`, `approve` and `reject`.
  - External providers include RetainDB and ByteRover (bundled), plus Honcho, Hindsight, Supermemory, Mem0, OpenViking and Holographic (installable).

  — [Hermes docs: Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- Only one external memory provider can be active at a time, set through `memory.provider` in `~/.hermes/config.yaml`. Built-in memory always stays active. Providers prefetch before turns, sync turns, extract memories at session end and add tools. They are activated by `memory.provider`, not by `plugins.enabled`. — [Hermes docs: Memory providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers)
- hermes-dreaming integration:
  - Uses the Agent Plugins v1 format (`plugin.json` plus `skills/dreaming/`) and registers **no** tools, hooks, middleware or env vars.
  - Cron jobs are bound to its skill with only the memory toolset.
  - Install: `hermes plugins install hermes-dreaming` and `hermes plugins enable hermes-dreaming`, then `install.py`, which copies gate scripts to `~/.hermes/scripts/` and seeds `dreaming.json`. `install_cron.py` creates 2 agent jobs and 1 no-model sweep.
  - Requires Hermes ≥ 0.21 and Python ≥ 3.9.

  — [Hermes docs](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- hermes-dreaming depends on the "holographic" fact-store plugin for several features. The README says holographic "left the Hermes core on 2026-10-11" and is now maintained separately. The docs warn that enabling holographic opens a fact-store write path that `memory.write_approval` does not cover. — [GitHub README](https://github.com/itpartypattaya/hermes-dreaming); [Hermes docs](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- mindhall integration (`__init__.py`):
  - `register(ctx)` calls `ctx.register_tool(..., toolset="mindhall")` for `mindhall_read`, `mindhall_update_work`, `mindhall_set_date`, `mindhall_add_note` and `mindhall_remove`.
  - It also registers `ctx.register_hook("pre_llm_call", inject)`, `ctx.register_hook("post_compaction", carry_over)`, `ctx.register_system_prompt_section("mindhall.rules", ..., position="after_memory", max_chars=1200)` and the `/mindhall` command.
  - The Hermes signer is `MINDHALL_AGENT_NAME` from the profile `.env`, otherwise "Hermes <Profile>".

  — [__init__.py](https://raw.githubusercontent.com/jai-srinivas/mindhall/main/__init__.py)
- mindhall install: `hermes plugins install` for the plugin, then a gateway restart. Updates use `hermes plugins update mindhall`. The MCP server is run separately as a service. — [README](https://github.com/jai-srinivas/mindhall)

### Inferences
- Because neither project takes the single provider slot, both could in principle sit alongside an external provider. hermes-dreaming even relies on holographic as its fact source.
- mindhall's `pre_llm_call` injection adds tokens to every turn (the rules section is capped at 1,200 chars, plus the context block).

### Gaps
- I did not fetch the developer guide on the MemoryProvider interface, so its method names are unconfirmed.

## 5. License, maturity, activity, red flags

### Takeaway
hermes-dreaming is small but genuinely maintained. It has had about 3 months of work, 154 commits, 30 version tags (v2.9.9 to v3.8.6), CI, tests and a listing in the official catalog. mindhall is a 4-day-old solo project. Its history is mostly "Add files via upload" commits, it has one tag (v0.3.2), and its "signed log" claim overstates what the code does. Both are MIT-licensed, and both show AI co-authorship in at least one commit.

### Cited Findings
- hermes-dreaming:
  - 154 commits on main, 23 stars, 3 forks, MIT.
  - CI in `.github/workflows/` runs ruff and checks the vendored screen against upstream.
  - A `tests/` directory uses stdlib unittest with synthetic data and no network.
  - README in English and Russian, plus a CHANGELOG.
  - The Releases section is empty, but tags exist.

  — [GitHub repo](https://github.com/itpartypattaya/hermes-dreaming)
- hermes-dreaming has 30 tags, from v2.9.9 to v3.8.6 (the latest). — [GitHub API tags](https://api.github.com/repos/itpartypattaya/hermes-dreaming/tags)
- The latest hermes-dreaming commits date from 2026-11-07, including "release 3.8.6" and merges of PRs #30–#32 (for example `fix/codex-review-385`). The "release 3.8.6" commit carries a "Co-Authored-By: Claude Opus 5.5" trailer. — [GitHub API commits](https://api.github.com/repos/itpartypattaya/hermes-dreaming/commits?per_page=5)
- mindhall:
  - About 27 commits on main, no releases, 1 tag (v0.3.2), 0 stars and 0 forks.
  - Has a `tests/` directory covering the engine and settings with pytest.

  — [GitHub repo](https://github.com/jai-srinivas/mindhall); [GitHub API tags](https://api.github.com/repos/jai-srinivas/mindhall/tags)
- mindhall commit history runs from 2026-11-07 to 2026-11-10. Of the visible commits, 14 are "Add files via upload" and several are deletes (for example of `mindhall-v0.2.0.zip`, `test_engine.py` and `catalog-entry.yaml`). There is one PR merge, of #1 from the `dev` branch. The commit "Keep same-named dates per project, hide secret from logs, local times" has a "Co-Authored-By: Claude Opus 5.5" trailer. — [GitHub API commits](https://api.github.com/repos/jai-srinivas/mindhall/commits?per_page=100)

### Inferences
- Red flags for mindhall:
  - Very new (created 4 days before the carousel), with a single author under two names.
  - Code was uploaded through the web UI as zipped or loose files, not developed incrementally in git.
  - The "signed change log" is attribution only.
  - Authentication is a URL secret.
  - Signer names are self-declared by clients.
  - There is no community validation.
- Red flags for hermes-dreaming:
  - Single maintainer.
  - The judge's accuracy figures come from a model-written, human-unchecked holdout.
  - It depends on an out-of-core plugin (holographic).
  - It uses frontier third-party judge models (Jev via OpenRouter, OpenAI) if enabled.
  - The cron agent jobs send up to 40k characters of human chat to the configured model nightly.
  - The README itself is candid about these limits, which is a positive sign.
- The carousel's figures (23 stars; 0/0/1 contributor) are accurate as of 2026-11-11. The carousel offers no independent verification of either project's quality.

### Gaps
- Last commit date for mindhall is 2026-11-10 per the API's pushed_at. I could not see the final roughly 18k characters of the commits API response, so a few commit messages are unread.
- I did not check the contributor count for hermes-dreaming; the page did not show it.
- I did not check the open issue's content.
