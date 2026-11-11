# ZeroMem and Recall: memory add-ons for Hermes Agent (state as of 2026-11-11)

## Q1. What are the exact repos, and do they match the carousel?

### Takeaway
Both are real plugins in the official Hermes Agent plugin marketplace. ZeroMem is `ptaranat/zeromem` by Panat Taranat: a Rust port of the arXiv paper "Zero-Mem", MIT, 20 stars, which matches the carousel's "~20 stars". Recall is `memeshee/hermes-recall` by GitHub user memeshee: Python, MIT, created 2026-11-06, with 0 stars and 6 commits. The carousel's descriptions match both listings. The carousel's "zero model calls" for ZeroMem overstates it: the plugin makes no LLM calls, but it runs a local embedding model by default.

### Cited Findings
- ZeroMem marketplace entry: author ptaranat, repo github.com/ptaranat/zeromem, v0.4.0, "Local memory that keeps every message word for word in one SQLite file", install with `hermes plugins install zeromem`, requires Hermes >=0.22.0. — [Hermes marketplace: zeromem](https://hermes-agent.nousresearch.com/marketplace/zeromem)
- GitHub API for ptaranat/zeromem: created 2026-08-05, pushed 2026-11-10, 20 stars, 6 forks, 0 open issues, MIT, language Rust. Description: "A Rust port of the Zero-Mem approach (arXiv:2607.29377)…stores all messages verbatim in one SQLite file and searches them without LLM calls, for use with Hermes Agent". Topics: agent-memory, hermes-agent, rust. — [GitHub API](https://api.github.com/repos/ptaranat/zeromem)
- The repo page shows 32 commits on `main` and no GitHub Releases. It has a CHANGELOG. — [GitHub repo](https://github.com/ptaranat/zeromem)
- PyPI package `zeromem`: 0.4.0 (2026-11-05) and 0.4.1 (2026-11-10). Prebuilt cp39-abi3 wheels for macOS x86_64/arm64, manylinux x86_64/aarch64 and Windows amd64. Author email lists Panat Taranat. Summary: "Zero-token memory for LLM agents… Rust core, single SQLite file". — [PyPI JSON](https://pypi.org/pypi/zeromem/json)
- Source paper: "Zero-Mem: Zero-Token Memory Operations for LLM Agents", Xiao et al., arXiv:2607.29377, submitted 2026-07-31. The source of record is raw interaction traces, viewed through an entity–context graph and a temporal hierarchy with query-dependent coordination and deterministic calibration. Only the final QA reader calls an LLM. The paper reports 57.6% lower memory-operation time than the fastest baseline. — [arXiv](https://arxiv.org/abs/2607.29377)
- The paper's official code is said to come to github.com/TheMoon0815/Zero-mem after peer review. The search snippet does not confirm it is public, and that repo is a different project from the Hermes plugin. — search result via [Emergent Mind](https://www.emergentmind.com/papers/2607.29377) (snippet only)
- An unrelated "ZeroMem" exists: an ETHGlobal project for encrypted memory on 0G. Don't confuse the two. — [ETHGlobal](https://ethglobal.com/showcase/zeromem-k89ud)
- Recall marketplace entry: author memeshee, repo github.com/memeshee/hermes-recall, v0.2.1, requires Hermes >=0.19.0, MIT. Install with `hermes plugins install recall`, then `hermes plugins enable recall`, then `/recall index ~/Documents`. — [Hermes marketplace: recall](https://hermes-agent.nousresearch.com/marketplace/recall)
- GitHub API for memeshee/hermes-recall: created 2026-11-06, pushed 2026-11-08, 0 stars, 0 forks, MIT, language Python, no topics. Description: "Local file recall for Hermes Agent: index the documents on your machine, search them by content, cite them by path." — [GitHub API](https://api.github.com/repos/memeshee/hermes-recall)
- The repo has 6 commits on `master`, no releases, and no listed contributors. — [GitHub repo](https://github.com/memeshee/hermes-recall)

### Inferences
- The carousel's "Recall" is the Hermes plugin `recall` from memeshee. It is not Microsoft Recall and not the other "Recall" projects (for example the Gemini+ChromaDB tool on shiporskip).
- Recall was about 5 days old at research time. The carousel promoted a brand-new plugin with zero stars.

### Gaps
- I did not view the Instagram carousel directly. The match rests on the user's description and on the marketplace text, which closely mirrors it (the "acme invoice" example and the `[recall]` prefix).
- I did not check Reddit or X discussion of either plugin.

## Q2. ZeroMem: how it works, what "zero model calls" means, ranking, size and pruning

### Takeaway
"Zero model calls" means zero LLM calls (zero tokens) for storing and searching memory. It does not mean zero model inference. By default ZeroMem embeds every turn locally with bge-small-en-v1.5 through fastembed, a model of about 130 MB downloaded from Hugging Face on first run. There is an offline hash-embedder fallback (`use_model: false`). Retrieval is hybrid and deterministic in Rust: in-memory BM25 plus dense vectors, a graph view (PPR) and a hierarchical/timeline view, then fusion and linked-turn expansion. Storage is a single SQLite file with no FTS5. There is no automatic pruning and no character or token cap on injected recall.

### Cited Findings
- Storage: one SQLite file at `~/.hermes/memory/zeromem.db` holds every user and assistant message as plain text. Writes happen in a background thread. — [marketplace](https://hermes-agent.nousresearch.com/marketplace/zeromem)
- Schema in `store.rs`:
  - `turns(id, session_id, session_turn, speaker, text, ts, source_uuid)`, with a unique partial index on `source_uuid` for dedup.
  - `embeddings(kind, key, vec BLOB, turn_id)`, vectors stored as little-endian f32.
  - `meta(key, value)`.
  - No FTS5 virtual table.
  - WAL mode, `synchronous=NORMAL`.
  - The graph, timeline and BM25 state are "derived from turns and rebuilt in memory on open". — [store.rs](https://raw.githubusercontent.com/ptaranat/zeromem/main/crates/zeromem/src/store.rs)
- BM25 is a custom in-memory Rust implementation with k1=1.2, b=0.75 and non-negative IDF `ln((n-df+0.5)/(df+0.5)+1)`, plus a phrase-match counter for names, dates, numbers and quotes. — [lexical.rs](https://raw.githubusercontent.com/ptaranat/zeromem/main/crates/zeromem/src/lexical.rs)
- Pipeline from the README: each query gets a deterministic profile, is routed to a primary view, and runs both the graph view (PPR) and the hierarchical view. Scores are fused (paper eq. 12-13, `fuse.rs`) and linked turns are appended. The README says the BM25 in the graph view was informed by reading the official code. — [README](https://github.com/ptaranat/zeromem)
- Crate modules include `ner.rs`, `graph.rs`, `graph_view.rs`, `hier_view.rs`, `route.rs`, `fuse.rs`, `calibrate.rs`, `embed.rs`, `lexical.rs` and `mcp.rs`. The repo also ships a Claude Code plugin (`.claude-plugin`, `claude/zeromem/.mcp.json`, `hooks.json`) and a `zm` CLI. — [repo tree](https://api.github.com/repos/ptaranat/zeromem/git/trees/main?recursive=1)
- Embeddings:
  - Default is bge-small-en-v1.5 via fastembed; multilingual-e5-small is an option for non-English text.
  - A deterministic hash embedder is the offline fallback and is used by the tests (`just test`).
  - Switching models re-embeds every turn. — [README](https://github.com/ptaranat/zeromem); [`__init__.py`](https://raw.githubusercontent.com/ptaranat/zeromem/main/hermes/zeromem/__init__.py)
- Hermes integration as a MemoryProvider (`memory.provider: zeromem` in config.yaml), class `ZeroMemProvider`:
  - Implements `is_available`, `initialize`, `system_prompt_block`, `prefetch`/`queue_prefetch`, `sync_turn`, `get_tool_schemas`/`handle_tool_call`, `on_session_switch`, `shutdown`, `get_config_schema`/`save_config` and `register(ctx)`.
  - `queue_prefetch` runs recall on a daemon thread. `prefetch` pops the cached block, or computes it synchronously.
  - Recall excludes the current session and returns one line per evidence item: session, turn, speaker, date, text.
  - `sync_turn` enqueues turns for a `zeromem-writer` thread.
  - Non-primary contexts are read-only. — [`__init__.py`](https://raw.githubusercontent.com/ptaranat/zeromem/main/hermes/zeromem/__init__.py)
- Tools: `zeromem_recall` (default `top_k` 5), `zeromem_stats`, `zeromem_forget_session`. Import of existing history: `hermes zeromem import` (preview), then `--yes`. It reads `hermes sessions export` and is idempotent. — [marketplace](https://hermes-agent.nousresearch.com/marketplace/zeromem)
- Token budget:
  - The plugin itself does not truncate injected recall by characters or tokens.
  - Pre-turn recall passes `top_k=None`, so the library default applies.
  - README scale: about 130 words at top_k 5, about 3,000 words at top_k 50. — [`__init__.py`](https://raw.githubusercontent.com/ptaranat/zeromem/main/hermes/zeromem/__init__.py); [README](https://github.com/ptaranat/zeromem)
- Pruning: there is no automatic pruning, TTL, size limit or `VACUUM`. The only deletion is `zeromem_forget_session` (one session's turns, graph state and embeddings; refused for the active session), plus an orphan-embedding sweep. — [`__init__.py`](https://raw.githubusercontent.com/ptaranat/zeromem/main/hermes/zeromem/__init__.py); [store.rs](https://raw.githubusercontent.com/ptaranat/zeromem/main/crates/zeromem/src/store.rs)
- Author benchmark: LoCoMo evidence recall over 1,536 questions. This measures retrieval, not answer quality, and the author benchmarked no other memory systems.

  | Retriever | Recall | Context size |
  |---|---|---|
  | Official Zero-Mem | 0.848 | ~2,750 words |
  | zeromem, top_k 50 | 0.821 | ~3,000 words |
  | BM25 over turns | 0.732 | ~3,000 words |
  | zeromem, top_k 5 (default) | 0.573 | ~130 words |

  — [README](https://github.com/ptaranat/zeromem)
- Marketplace disclosures:
  - Installs a compiled Rust extension from PyPI.
  - Stores all messages in plaintext.
  - Recalls them verbatim across all sessions of the profile, including all chats and senders on a gateway.
  - The agent can permanently delete a past session's turns. — [marketplace](https://hermes-agent.nousresearch.com/marketplace/zeromem)

### Inferences
- The file grows without bound: one text row plus one 384-dim f32 vector per turn, about 1.5 KB per vector, plus entity embeddings. Because indexes are rebuilt in memory on open, startup time and RAM grow with history.
- The default top_k=5 gives only 0.573 evidence recall. That is cheap in tokens, but it misses much. Raising top_k gets close to the paper's numbers at about 20x the context.
- The cross-session, cross-sender verbatim recall on a gateway is a privacy and leakage risk in multi-user setups.

### Gaps
- I did not read `fuse.rs`, `route.rs` or `calibrate.rs`, so the exact fusion weights and the calibration rules are not verified.
- The library default for top_k when `None` is passed is not confirmed.
- The test count and CI coverage are not stated. There is `crates/zeromem/tests/pipeline.rs` and a release workflow.

## Q3. Recall: injection logic, formats and parsers, indexing

### Takeaway
Recall is a pure-Python, mostly standard-library Hermes plugin. It extracts document text into a SQLite FTS5 index (`unicode61` tokenizer, lexical BM25 plus path, filename, recency and phrase boosts, no embeddings). A `pre_llm_call` hook injects a block of at most 900 characters, starting with `[recall]`, that lists up to 3 candidate paths. It fires only on messages with document or lookup cues, at least 2 content tokens and a score of at least 3.5. The model must then call `recall_open` to read the file. There is no OCR. Indexing is incremental by mtime and size, with a bounded refresh at session start. It does not watch the filesystem.

### Cited Findings
- Hermes surfaces used:
  - `ctx.register_hook("pre_llm_call")` for the ambient hint.
  - `ctx.register_hook("on_session_start")` for a bounded background refresh.
  - `ctx.register_context_reference` for `@recall:<query>`.
  - Five tools: `recall_index`, `recall_search`, `recall_open` (paged with `offset`/`max_chars`), `recall_stats` and `recall_forget`.
  - A `/recall` slash command.
  - Files: `extract.py`, `guard.py`, `hooks.py`, `indexer.py`, `refresh.py`, `refs.py`, `runtime.py`, `store.py`, `tools.py`, `plugin.yaml`, `skills/recall/`, `tests/`. — [repo](https://github.com/memeshee/hermes-recall); [marketplace](https://hermes-agent.nousresearch.com/marketplace/recall)
- Ambient hook (`hooks.py`):
  - **Cues:** `DOC_CUES` (file, invoice, contract, lease, pdf, spreadsheet…) or `LOOKUP_CUES` ("where is", "find my", "pull up", "in my documents") or a quoted string.
  - **Tokens:** alphanumeric runs of 3+ characters, stopwords removed. At least 2 tokens are needed; the query uses the first 8. Search returns 6 hits.
  - **Limits:** `MIN_SCORE = 3.5`, `max_hints` default 3, `MAX_CONTEXT_CHARS = 900`, each snippet capped at 180 characters.
  - **Output:** header "[recall] Local files in the user's index that may be the document being discussed:", then lines `- {path} (modified {date}; {filename}) — "{snippet}"`. The closing instruction tells the model to call `recall_open`, cite the path, and say so if nothing matches. The hook returns `{"context": block}` to Hermes.
  - **Dedup:** the same path is not shown twice per session. The map resets after 400 sessions.
  - **Skips:** messages shorter than 12 characters, `/` commands, gateway, cron and background markers, and messages already containing `@recall:`, `@file:` or `@folder:`.
  - **Failure handling:** errors are swallowed and return `None`.
  - **Switch:** the `ambient` setting turns the hook off. — [hooks.py](https://raw.githubusercontent.com/memeshee/hermes-recall/master/hooks.py)
- Extraction (`extract.py`):
  - **PDF:** optional `pypdf` (first 200 pages) if installed. Otherwise a stdlib fallback that inflates `stream…endstream` with zlib and pulls `(literal)` and `<hex>` strings. Under 24 characters means "no text layer".
  - **OOXML/ODF:** `zipfile` plus regex on `<w:t>`, `<a:t>`, `sharedStrings`/sheet XML and ODF `content.xml`.
  - **HTML:** regex tag-stripping.
  - **.eml:** read as plain text, with no MIME decoding.
  - **Limits:** 8 MB per file, 8 MB per zip member, 4 MB per inflated PDF stream, 4,000 spreadsheet cells.
  - **Chunks:** 1,200 characters with 150 overlap.
  - **Formats:** about 45 text and code extensions plus .docx/.xlsx/.pptx/.odt/.ods/.odp/.pdf. — [extract.py](https://raw.githubusercontent.com/memeshee/hermes-recall/master/extract.py)
- Store (`store.py`):
  - **Tables:** `files(path, mtime, size, ext, chunks, skipped)`, `chunks(id, file_id, ord, text)`, and FTS5 `chunks_fts(text, path/file_id/ord UNINDEXED)` with tokenizer `unicode61 remove_diacritics 2`.
  - **Query:** OR of `tok` and `tok*`.
  - **Scoring:** −bm25, +2.5 per token found in the path, +3.0 for a filename hit, ×(1+0.35/(1+age_days/90)) for recency, +3.0 for an in-order phrase hit.
  - **Re-indexing:** a full drop and re-insert per changed file. — [store.py](https://raw.githubusercontent.com/memeshee/hermes-recall/master/store.py)
- Indexing defaults:
  - roots `~/Documents`, `max_files` 20,000, `budget_s` 90, `max_file_mb` 8.
  - `refresh_on_start` true, with a 25 s and 5,000-file cap.
  - Incremental by mtime and size. Deleted files are dropped on the next scan. Bounded runs report `partial: true`.
  - Author's measurement: 4,127 files and 101,483 passages in 73 s; queries 187–536 ms; a no-change re-run takes 0.3 s. — [repo](https://github.com/memeshee/hermes-recall); [marketplace](https://hermes-agent.nousresearch.com/marketplace/recall)
- Security and policy:
  - Credential files (`.env`, `*.pem`, `id_rsa`, `.ssh`, `.aws`, `auth.json`, `state.db`), `.hermes` home and `/proc` are refused after symlink resolution.
  - `recall_open` and `@recall:` can read any absolute path outside that refused set.
  - The index is plaintext and unencrypted at `~/.hermes/plugin-data/recall/`.
  - Passwords inside ordinary text files are still indexed.
  - No OCR.
  - One index per profile. — [marketplace](https://hermes-agent.nousresearch.com/marketplace/recall)
- Tests: `tests/selftest.py` holds 30 stdlib-only behavioural checks covering ranking, extraction, the denylist, incremental indexing, the 4 ambient-hook rules and read-policy edge cases. — [repo](https://github.com/memeshee/hermes-recall)

### Inferences
- The docs say "standard library only", but `extract.py` optionally uses `pypdf`. This is a minor documentation mismatch. The marketplace also claims .eml support, but email is only read as raw text.
- The regex-based XML and PDF extraction is fragile. Content streams with CID fonts or custom encodings will produce garbled text or no text. Quality is likely much lower than pypdf, pdfminer or python-docx.
- Lexical-only search has two consequences. Synonyms fail. The `unicode61` tokenizer without stemming also means "invoices" and "invoice" match only through the `tok*` prefix.

### Gaps
- I did not read `refresh.py`, `indexer.py` or `guard.py`, so the exact on-session-start refresh mechanics are unverified. `hooks.py` contains no refresh code.
- There is no published token budget beyond the 900-character cap on the hint. The size of `recall_open`'s default `max_chars` is not verified.

## Q4. Maturity and red flags

### Takeaway
ZeroMem is young but credible: 3 months old, 32 commits, paper-backed, with PyPI wheels and a published benchmark. Recall is very immature: 5 days old, 6 commits, 0 stars, one author. Both store sensitive data in plaintext.

### Cited Findings
- ZeroMem: 20 stars, 6 forks, 32 commits, last push 2026-11-10, MIT, PyPI 0.4.1. No GitHub Releases (releases go through a PyPI workflow). — [GitHub API](https://api.github.com/repos/ptaranat/zeromem); [PyPI](https://pypi.org/pypi/zeromem/json)
- Recall: 0 stars, 0 forks, 6 commits, created 2026-11-06, last push 2026-11-08, MIT, no releases. Marketplace v0.2.1. — [GitHub API](https://api.github.com/repos/memeshee/hermes-recall)

### Inferences
- **ZeroMem red flags:**
  - The marketing says "zero model calls", yet it downloads and runs a 130 MB embedding model by default.
  - No retention or pruning.
  - No cap on injected text.
  - Verbatim cross-session and cross-sender recall on gateways.
  - A compiled native extension (supply-chain trust in one maintainer).
  - Default top_k=5 gives only 0.573 evidence recall.
  - It is a third-party port, not the paper authors' code.
- **Recall red flags:**
  - Brand-new and single-author.
  - `recall_open` can read any absolute path the model gives it, which could be abused through prompt injection.
  - The index is a plaintext copy of document contents.
  - Homemade PDF and Office parsers.
  - No OCR.
  - Small doc/code mismatches (pypdf, .eml).
- Relevance to devbrain: both follow the same "no LLM in the core" principle as devbrain. Recall's design maps closely to devbrain's FTS5 approach: a pre-turn hint capped in characters, a cue-gated trigger, per-session dedup, and "hint only, the model must open the file to cite it". ZeroMem's verbatim-turns-as-source-of-truth, with derived indexes rebuilt on open, is a pattern worth noting.

### Gaps
- Independent reviews and community uptake (Reddit, X, Discord) were not checked.
- I did not confirm whether the carousel's star counts were measured at the same date.
