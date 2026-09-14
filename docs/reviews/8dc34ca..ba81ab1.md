## Review Record

**Source**: git range `8dc34ca..ba81ab1`（單一提交 `ba81ab1 refactor(validate): read the format from a schema the collection fills`），本機 `git diff` 解析，未取用任何遠端 PR/MR 資料
**Calibration**: Gates 1-7（`scripts/validate_skills.py` 與 `scripts/skill_model.py` 是隨 release tag 出貨的結構性強制機制，屬 shared library / production path；本次改動不觸及認證、加密、命令執行或使用者輸入邊界，故不開 Gate 8）
**Triage**: skipped（scope 為 3 個檔案，未達 5 個檔案的門檻）
**Coverage**: partial — gate-reviewed: 無；partially-gate-reviewed（皆為 Gates 1-2，階梯在 Gate 2 關閉）: `skill_model` module docstring、`skill_model.FormatSchema`、`skill_model.FORNAX_FORMAT`、`skill_model.NAME_PATTERN`/`FAMILIES`/`STATUSES`/`HANDOFF` 四個 module alias、`validate_skills` module docstring、`validate_skills.INPUT_LINE` 註解、`validate_skills.validate_handoffs`、`validate_skills.validate_skill_manifest`、`validate_skills.validate_skill_document`、`validate_skills.validate_skill`、`validate_skills.main`、`test_validate_skills.check`、`test_validate_skills.check_skill_against`、`test_validate_skills.SchemaSeamTests`（三個 test method）、`test_validate_skills.ValidateSkillTests.test_missing_required_field_fails`、`test_validate_skills.SkillModelTests.test_the_shared_fixture_satisfies_every_required_field`；triage-only: 無；unread: 無
**Findings**: 7（Gate 2 兩列、Against-Contract 三列 VIOLATED、Structural Causes 兩列 case-2 結構觀察；Claims Verified 的 REFUTED 列與 Ledger 列不計入）
**Verdict**: FAIL at Gate 2 + CONTRACT-VIOLATED
**Not executed**: static review only — 測試 / build / runtime 未執行。`Behaviour is unchanged` 的逐值比對是靜態對照 `8dc34ca` 的字面值完成的；「restored tree is green」需要 runtime pass 才能結案。

### Gate Index

| Gate | Focus | Status |
|---:|---|---|
| 1 | Formatting & Syntax Hygiene | pass |
| 2 | Naming & Readability | fail |
| 3 | Error Handling & Observability | blocked |
| 4 | Control Flow & Structural Clarity | blocked |
| 5 | Responsibility & Boundaries | blocked |
| 6 | Business Logic Integrity | blocked |
| 7 | Deduplication & Composition | blocked |
| 8 | Security & Parameter Integrity | not inspected |

Gate 1 判準來源：`ruff.toml`（width 100、`E`/`F`/`W`/`PGH004`/`RUF100`、preview on）。三個檔案無超過 100 字元的行、無未使用 import（`dataclasses.replace`、`FormatSchema`、`FORNAX_FORMAT`、`listed` 皆有讀者）、無 debug 殘留、無註解掉的程式碼。Gate 3-7 的判準來源（AGENTS.md、PROJECT.md、`docs/skill-yaml-schema.md`）已於 Phase 3 定位，但階梯在 Gate 2 關閉，故其讀數未取得；Phase 3 已到手的結構觀察列於 Structural Causes。

### Against-Contract

| # | Clause | Falsifier attempted | Result | Evidence |
|---|---|---|---|---|
| 1 | AGENTS.md Script And Dependency Policy：「When a module takes ownership of a behaviour, enumerate every existing implementation of it.」 | 逐一列舉樹內每個 skill 名稱文法的拼法，看有沒有既沒被導向新 owner、也沒被記錄為刻意留在外面的 | **VIOLATED** | `scripts/skill_model.py:22`（列舉只寫了 `development_knowns.py` 與 `skill_interface.py`）對照 `scripts/validate_skills.py:75`（`RECORD_INPUT_PATTERN` 的 `producer` group 就是 skill 名稱，`[a-z0-9]+(?:-[a-z0-9]+)*`，而且就在本次改為讀 schema 的同一個檔案裡）、`scripts/skill_model.py:89`（`handoff` 自己的 capture group 把 skill 名稱再拼了一次 `[a-z0-9-]+`，就在 `name_pattern` 隔壁）、`scripts/seam_contract.py:55` |
| 2 | AGENTS.md Repository Hygiene：「a claim nothing reads … removing is a repair」 | 找出本次留下的、沒有任何讀者的名字 | **VIOLATED** | `scripts/validate_skills.py:604` — `main(schema=…)` 沒有呼叫者、沒有 CLI 旗標、沒有測試；`scripts/check_workspace.py:41` 與 `tools/fornax-cli/fornax_cli/cli.py:39` 都以 subprocess 呼叫，三個 seam 測試只到 `validate_skill`。對照同一 docstring 裡 `root` 參數的先例（`scripts/validate_skills.py:606`），那個是有測試讀的 |
| 3 | PROJECT.md：「`family` is a flat field …, the single source for README grouping and the generated skill maps」 | 以 `main(argv, root, replace(FORNAX_FORMAT, families={"archaeology": …}))` 跑驗證，再跑 `skill_graph` | **VIOLATED**（在非預設 schema 下；在 `FORNAX_FORMAT` 下 holds） | `scripts/skill_graph.py:38,73,99` 讀的是 module alias 而非 schema，`scripts/distribution_manifest.py:26,349` 同理讀 `NAME_PATTERN`。validate 會放行的 family，`skill_graph.load` 會拒絕並從所有圖表中刪掉；falsifier 正是本提交宣稱要新增的能力 |
| 4 | AGENTS.md Repository Hygiene：「Do not write a count of what the repository contains.」 | 掃描新寫的 docstring 與 commit message 中每個緊鄰樹內名詞的數字、以及用字寫出的總數 | holds | commit message「Three cases assert the seam」數的是這個 commit 加了什麼，落在該條的 commit-prose 除外；`scripts/skill_model.py:7` 用 "Several"、`scripts/skill_model.py:52` 用 "more than one spelling"、`scripts/validate_skills.py:22` 用 "Several" —— 皆為規則指定的替代寫法。`scripts/skill_model.py:18` 的 "the two" 指的是句子自己命名的兩個角色（alias 與 schema field），不是對樹的計數 |
| 5 | AGENTS.md Repository Hygiene：「Do not cite a line number in durable prose.」 | 在新增的 docstring、註解與 commit message 中搜尋 `path:line` 形式 | holds | `scripts/skill_model.py:1-37`、`scripts/skill_model.py:48-65`、`scripts/validate_skills.py:18-25`、`scripts/validate_skills.py:69-72`、`scripts/tests/test_validate_skills.py:1740-1750` 全部只引符號與檔名。`check_citations.SUBJECTS` 涵蓋的檔案本次未被改動 |
| 6 | AGENTS.md Repository Hygiene：「Before adding a check, say what it would have caught and what it costs per change.」 | 找出本次新增、需要交代歷史失敗與每次改動成本的檢查 | holds | `scripts/validate_skills.py:376`、`:389`、`:394`、`:407`、`:470`、`:475` 都是原檢查換讀 schema，判準與訊息不變；新增的三個是測試不是檢查 |
| 7 | AGENTS.md Testing Strategy：「Check the fixture actually fails when the rule is removed … Revert the unit the claim names, not something it calls.」 | 對每個 seam 測試，把對應字面值還原進 `validate_skills`，看測試是否真的轉紅 | holds | `scripts/tests/test_validate_skills.py:1752`（還原 `version` 禁令 → `allowed` 為 False → `assertTrue` 失敗）、`:1767`（還原無條件的 `INPUT_LINE` 檢查 → `optional` 為 False → 失敗）、`:1784`（還原 `FAMILIES` 查表 → `known` 為 False → 失敗）。三者都經 `check()` 走 `validate_skill`，也就是所有權真正搬走的那個消費者，不是它呼叫的東西 |
| 8 | AGENTS.md Testing Strategy：hand-written matcher 需要兩個 negative control（near-miss 同前綴、valid alternate spelling） | 找出本次新增、對某個文法宣稱不變式的手寫 matcher | holds（空集合） | 兩個 `re.compile` 逐字搬移（`scripts/skill_model.py:80`、`:88`），文法未改；本次沒有新的手寫 matcher |
| 9 | PROJECT.md：「Enforcement is the structural floor only.」 | 找出把 judgment 塞進驗證器的新欄位 | holds | `FormatSchema` 的欄位（`scripts/skill_model.py:67-76`）全是結構性詞彙與必填/禁填集合，沒有描述品質或散文清晰度 |
| 10 | AGENTS.md Commit Classification：`refactor` 是否為正確型別（`fix > feat > build > test > refactor > docs > chore`） | 問這次是否加了 "a new reusable script capability"，若是則應為 `feat` | holds（張力已記錄） | 對出貨的 collection 而言外部行為不變，且新 seam 從 CLI 完全不可達（見上面第 2 列）—— 正因為沒有讀者，它還構不成 `feat`。這兩件事互為表裡：把 seam 接上讀者，型別就該改成 `feat` |
| 11 | AGENTS.md Final Report Notes：commit 不得含 AI 署名/共同作者 | 檢查 `ba81ab1` 的 trailers 與作者 | holds | trailers 為空，author `tacticaldoll` |
| 12 | AGENTS.md Versioning / PROJECT.md「Release bumps are separate」 | 檢查此提交是否動到 `distribution.json` 或 host manifest 版本 | holds | `git diff --stat` 僅三個 `scripts/` 檔案 |
| 13 | AGENTS.md Authoring Workflow 第 6 步：「Run repository validation before reporting completion」 | 在 scope 內找執行紀錄 | unprovable statically | scope 只含原始碼；這是流程條款，靜態檢視無法證否 |

### Claims Verified

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | 「Behaviour is unchanged: every value FORNAX_FORMAT carries is the one the validator held.」 | `scripts/skill_model.py:79-101` 對照 `8dc34ca` 的 `scripts/validate_skills.py` 原字面值：`name_pattern`、`families`、`statuses`、`handoff`、`required_manifest_fields`、`block_manifest_fields`、`description_prefix`、`requires_input_line`、`resource_keys` 逐一相同；`forbidden_manifest_fields` 的兩段在 `scripts/validate_skills.py:377` 組回的字串與原訊息逐字相同；檢查順序也未移動 | verified |
| 2 | 「FAMILIES, STATUSES, NAME_PATTERN and HANDOFF stay module names, so the sibling scripts and the prose that cite them keep resolving」 | `NAME_PATTERN` 由 `scripts/distribution_manifest.py:349` 讀、AGENTS.md 與 `scripts/evidence_currency.py:185` 引；`FAMILIES`、`HANDOFF` 由 `scripts/skill_graph.py:73,89` 讀。但 `STATUSES`（`scripts/skill_model.py:105`）沒有任何 sibling script 讀、也沒有任何散文引，唯一讀者是 `scripts/tests/test_validate_skills.py:219` | partial |
| 3 | 「each is bound to the schema's own field rather than restating it, so the two cannot drift」 | `scripts/skill_model.py:103-106` 四個 alias 都是繫結而非重述 | verified |
| 4 | 「Three cases assert the seam by keeping one input fixed and changing only the schema … each asserts the refusal under FORNAX_FORMAT in the same breath」 | `scripts/tests/test_validate_skills.py:1752`、`:1767`、`:1784`，三者都是 `assertFalse(...)` + `assertIn(訊息)` + `assertTrue(變體通過)` 的成對斷言 | verified |
| 5 | 「Each was mutation-checked: restoring the literal … turns the suite red」 | 見 Against-Contract 第 7 列；三次還原各自使對應測試的寬鬆半邊失敗，屬構造上必然 | verified |
| 6 | 「and the restored tree is green」 | scope 內無任何執行證據 | REFUTED |
| 7 | 「The **Input**: label grammar deliberately did not move … the schema carries only requires_input_line」 | `scripts/validate_skills.py:69-77` 的註解就地記錄了理由，`scripts/skill_model.py:60-65` 也在 `FormatSchema` docstring 記了一次 | verified |
| 8 | 「the version prohibition arrived that way, spelled into the check that reads it」 | `8dc34ca` 的 `validate_skills` 確實內嵌 `version` 禁令；現由 `scripts/skill_model.py:95-97` 持有 | verified |

第 6 列的 `REFUTED` 是「reviewed scope 內沒有可定位的證據」，不是「該宣稱為假」。這是靜態檢視，要結案需要一次 runtime pass（handoff：`plan-testing` 或直接跑 `PYTHONPATH=scripts .venv/bin/python -m unittest discover -s scripts/tests`）。本 repo 的既有教訓正是「修好先跑再寫宣稱」，因此這一列不以「無法驗證」帶過。

### Structural Causes

| # | Finding | Cause (the thing to change) | Cause location | Gate that would carry it |
|---|---|---|---|---|
| 1 | Gate 2 #1、#2 | 把「定義」這個詞收回給 `FORNAX_FORMAT` 的欄位，讓舊段落只描述繫結；同一段對四個 alias 給的共同理由，要按每個 alias 實際的讀者分開寫 | `scripts/skill_model.py:13` | Gate 2 (fail) |
| 2 | Against-Contract #1 | 在 `FormatSchema` 接手 `name_pattern` 的同一處，把 skill 名稱文法的其餘拼法補進既有的列舉句，或把 `RECORD_INPUT_PATTERN` 的 `producer` group 改讀 `schema.name_pattern` | `scripts/skill_model.py:22` 與 `scripts/validate_skills.py:75` | Gate 1 (pass)／規則本身由 Against-Contract 承載 |
| 3 | Against-Contract #2、#3 | schema 只走到 `validate_skill` 為止；要讓「a collection can state a different filling」成立，seam 必須延伸到 `skill_graph.load` 與 `distribution_manifest`，或在宣稱處寫明這兩者被釘在 `FORNAX_FORMAT` 上 | `scripts/skill_model.py:4`（宣稱處）、`scripts/skill_graph.py:38`、`scripts/distribution_manifest.py:26` | Gate 5 (blocked) |
| 4 | — | `schema` 在五個函式上都是有預設值的參數，其中四個的預設永遠取不到（`validate_skill` 一路以位置引數傳遞）。預設留在內層檢查上，正是下一個呼叫者無聲拿回 `FORNAX_FORMAT` 的途徑 —— 與同檔 docstring 對 `root` 所寫的理由相反。改法：`validate_skill_manifest`、`validate_skill_document`、`validate_handoffs` 的 `schema` 改為必填，預設只留在 `validate_skill` 與 `main` | `scripts/validate_skills.py:181,347,428` | Gate 5 (blocked) |
| 5 | — | `FormatSchema` 宣稱 `Frozen because a check that reads a value must not be able to set it`，但 `families` 是普通 `dict`：`FORNAX_FORMAT.families["x"] = "X"` 會成功，而 `FAMILIES` 是同一個物件，所以任一處的就地改動會同時被 `validate_skills` 與 `skill_graph` 看見；同時 `hash(FORNAX_FORMAT)` 會丟 `TypeError`。改法：欄位型別改 `Mapping[str, str]`，以 `types.MappingProxyType({...})` 填入（`listed()` 與 `dataclasses.replace` 都不受影響） | `scripts/skill_model.py:68`、`:81`、`:104` | Gate 5 (blocked) |
| 6 | — | 測試套件內出現兩種「向 owner 問值」的拼法：已遷移處讀 `FORNAX_FORMAT.required_manifest_fields`，未遷移處仍讀 `skill_model.FAMILIES` / `skill_model.STATUSES`。改法：全部改讀 `FORNAX_FORMAT` 的欄位，`STATUSES` 的 alias 隨之可刪 | `scripts/tests/test_validate_skills.py:211,219,1667` 對照 `:195,1677` | Gate 7 (blocked) |

第 3-6 列是 Phase 3 結構萃取階段就已到手的讀數；階梯把 Gate 5 與 Gate 7 關掉，不代表這些成因要被扣住不說。它們沒有 gate 覆蓋的宣稱，每列都標了所屬 gate 的狀態。

### Responsibility & Dependency Ledger

Gate 5 未開啟（Gate Index：blocked by Gate 2）。依規定仍列出此表並說明未開啟的原因，而非省略。

| # | Unit | Its job (one clause) | Handed in | Reached directly |
|---|---|---|---|---|
| — | （空） | Gate 5 對本 scope 未開啟任何 unit | — | — |

本 gate 未開啟的 in-scope units，以及各自的原因（單一軸線：階梯關閉）：`skill_model.FormatSchema`、`skill_model.FORNAX_FORMAT`、`skill_model` 的四個 module alias、`validate_skills.validate_handoffs`、`validate_skills.validate_skill_manifest`、`validate_skills.validate_skill_document`、`validate_skills.validate_skill`、`validate_skills.main`、`test_validate_skills.check`、`test_validate_skills.check_skill_against`、`test_validate_skills.SchemaSeamTests` —— 全部是 Gate Index 在 Gate 2 關閉階梯所致，不是 Phase 2 分流（本 scope 未跑 triage），也不是 Phase 3 覆蓋集合（無 `triage-only`、無 `unread`）。

Rows in this section are not findings.

### Gate 2: Naming & Readability

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | `scripts/skill_model.py:13` | Gate 2：一個概念有兩個名字，而散文把錯的那個叫作定義。`FAMILIES is the single definition of the allowed family values`、`STATUSES is the single definition of the allowed status values`，以及未被本次改動觸及的 `scripts/skill_model.py:29`「`HANDOFF` is the single definition of how a skill writes a handoff」，在 `:103-106` 之後都已是繫結而非定義 —— 真正的單一定義是 `FORNAX_FORMAT` 的欄位。讀者照字面在 `FAMILIES` 上加一個 family，改到的是 alias 所指的同一個 dict，卻不會出現在 `FORNAX_FORMAT` 的字面宣告裡，下一個讀 schema 的人看不到它 | 把三句改寫為繫結語氣，例如「`FAMILIES` 繫結 `FORNAX_FORMAT.families`，新增 family 請改 `FORNAX_FORMAT` 的宣告」；`:29` 的 `HANDOFF` 段落同步改寫，它現在是全檔唯一仍宣稱自己是 single definition 而完全未被本次修訂的段落 |
| 2 | `scripts/skill_model.py:16` | Gate 2：「They, `NAME_PATTERN` and `HANDOFF` stay module names because sibling scripts and the prose that cites them read them there」把一個理由套在四個名字上，但對 `STATUSES` 不成立 —— 沒有 sibling script 讀它，也沒有散文引它，唯一讀者是 `scripts/tests/test_validate_skills.py:219`，而同一套件在 `:195`、`:1677` 已改為直接讀 `FORNAX_FORMAT`。敘述比樹能支撐的更寬，讀者無法從這句判斷哪個 alias 真的有外部讀者 | 兩擇一：（a）刪掉 `STATUSES` alias（`:105`），把 `:219` 改讀 `skill_model.FORNAX_FORMAT.statuses` —— Repository Hygiene 說 removing is a repair；（b）保留，但把理由逐個寫清楚：`NAME_PATTERN` 由 `distribution_manifest` 與 AGENTS.md 讀、`FAMILIES`／`HANDOFF` 由 `skill_graph` 讀、`STATUSES` 僅供測試 |

### Structural Appendix

**`skill_model.FormatSchema`**（`scripts/skill_model.py:46-76`）— frozen dataclass，10 個欄位，無方法、無行為。閉包/callback：無。I/O：無。巢狀深度：0。生命週期：一次性宣告的持久值。隱藏相依：無。異常：`families` 是唯一可變的欄位型別，與 docstring 的 frozen 理由相牴觸（Structural Causes #5）。

**`skill_model.FORNAX_FORMAT`**（`:79-101`）— 單一模組層級值，含兩個 `re.compile`。四個 module alias（`:103-106`）與它共用物件身分，因此 `families` 在任一名字下的就地改動對雙方可見。

**`validate_skills.validate_skill_manifest`**（`:342-419`）— 讀 schema 的 6 個欄位（required、block、forbidden、statuses、families、resource_keys），全部只做查表與比對；診斷一律經 `fail()` → `printable()`，`forbidden_manifest_fields` 的 `why` 字串插值同樣被 sanitize，`scripts/validate_skills.py:79`。I/O：無（manifest 文字由呼叫端讀入）。

**`validate_skills.validate_skill`**（`:481-581`）— 本次改動的 schema 中繼站，把 schema 以位置引數傳給三個下游。同一函式內仍有一條不經 schema 的名稱文法路徑：`validate_record_inputs(skill_dir, name, content)`（`:551`）背後是 `RECORD_INPUT_PATTERN`（`:75`），這是 Against-Contract #1 的證據所在。

**`validate_skills.main`**（`:601-641`）— 新增第三個參數 `schema`，只往下傳給 `validate_skill`；`parse_args` 未新增對應旗標，`check_workspace` 與 `tools/fornax-cli` 都以 subprocess 呼叫，故此 seam 在 scope 內無任何讀者（Against-Contract #2）。

**`test_validate_skills.SchemaSeamTests`**（`:1739-1799`）— 三個測試，形狀一致：固定輸入、只換 schema、雙向斷言（`FORNAX_FORMAT` 下拒絕 + 變體 schema 下放行）。涵蓋 `forbidden_manifest_fields`、`requires_input_line`、`families` 三個欄位；`name_pattern`、`handoff`、`statuses`、`required_manifest_fields`、`block_manifest_fields`、`description_prefix`、`resource_keys` 七個欄位的 seam 無測試，`main` 層級的 seam 無測試。
