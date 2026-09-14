## Review Record

**Source**: git range `ba81ab1..1a84428`（11 個提交：`6e90409`、`266a703`、`8b0c24c`、`b07e360`、`9861912`、`3e02433`、`9a17615`、`28d3c0f`、`aa93acd`、`c13678d`、`1a84428`），本機 `git diff` / `git show` 解析，未取用任何遠端 PR/MR 資料。45 個檔案。
**Calibration**: Gates 1-7（`scripts/validate_skills.py`、`scripts/skill_model.py` 與新 package `scripts/agent_skill_format/` 都隨 release tag 出貨，屬 shared library / production path；本次改動不觸及認證、加密、命令執行或使用者輸入邊界，故不開 Gate 8。與上一輪同一判準）
**Triage**: Red 0 / Yellow 10 / Green 35
**Coverage**: partial — gate-reviewed（Gates 1-7 依階梯逐一開啟）: `agent_skill_format/__init__` module docstring、`schema.FormatSchema`、`skill_model` module docstring、`skill_model.FORNAX_FORMAT`、`skill_model.NAME_PATTERN`/`FAMILIES`/`HANDOFF`、`validate_skills` module docstring、`validate_skills.undeclared_directories`、`validate_skills.validate_skill_manifest`、`validate_skills.validate_skill`、`validate_skills.main`、`distribution_manifest.validate_distribution`、`read_whole.shell_words` 與其 `TYPE_CHECKING` 匯入、`shell_script` 的 `read_whole` 匯入、`test_module_claims.MODULES`、`test_module_claims.imports`、`test_module_claims.third_party`、`test_module_claims.ModuleClaimTests`、`test_validate_skills.SchemaSeamTests`（八個 test method）、`test_validate_skills.check`/`check_skill_against`/`MANIFEST_WITH_REFERENCES`、`docs/dispositions/8dc34ca..ba81ab1.md` 的 Causes 表、Reach 說明段與 Self-check 表、`docs/reviews/8dc34ca..ba81ab1.md` 全文；partially-gate-reviewed: `agent_skill_format/skill_interface.py` module docstring 的 Usage 區塊（僅 Gate 1，階梯在該檔 Gate 1 關閉）、`docs/guards.md` 的 `Written 2026-09-14` 章節（僅 Gate 1，同上）；triage-only: 其餘 33 個僅有 import 字面重寫的檔案（`scripts/check_citations.py`、`check_sources.py`、`check_text.py`、`contract_revision.py`、`development_knowns.py`、`evidence_currency.py`、`generated_block.py`、`record_shape.py`、`runtime_contract.py`、`seam_contract.py`、`skill_graph.py`、`tests/fixtures.py`、`tests/test_*.py` 十二個、以及 `agent_skill_format/` 內純搬移的 `constrained_yaml.py`、`diagnostic_text.py`、`host_paths.py`、`markdown_links.py`、`outcome.py`、`path_boundary.py`、`skill_yaml.py`、`workspace_files.py`）；unread: 無
**Findings**: 15（Gate 1 兩列、Gate 2 三列、Gate 5 一列、Gate 7 一列、Against-Contract 五列 VIOLATED、Claims Verified 一列尚未在他處計入的 REFUTED、Structural Causes 兩列 case-2 結構觀察。不計入：Against-Contract 第 6 列（已記錄的既決餘量）、其餘 REFUTED 列（皆為上列 gate finding 的「宣稱」軸，同一缺陷不重複計數）、Ledger 列、`holds`/`verified` 列）
**Verdict**: FAIL at Gate 1 + CONTRACT-VIOLATED + CLAIM-REFUTED
**Not executed**: static review only — 測試 / build / runtime 未執行。所有「turns N red / measured」類宣稱均以靜態推理判讀，未實際還原與重跑；凡靜態不可判定者標為 `unprovable statically`。

### Gate Index

| Gate | Focus | Status |
|---:|---|---|
| 1 | Formatting & Syntax Hygiene | fail |
| 2 | Naming & Readability | fail |
| 3 | Error Handling & Observability | pass |
| 4 | Control Flow & Structural Clarity | pass |
| 5 | Responsibility & Boundaries | fail |
| 6 | Business Logic Integrity | pass |
| 7 | Deduplication & Composition | fail |
| 8 | Security & Parameter Integrity | not inspected |

階梯以**檔案**為主體逐檔關閉，索引取跨檔最壞值；逐檔解如下：

- Gate 1 判準來源：`ruff.toml`（width 100、`E`/`F`/`W`/`PGH004`/`RUF100`、preview on）。Gate 1 在 `scripts/agent_skill_format/skill_interface.py` 與 `docs/guards.md` 失敗，這兩個檔的 Gates 2-7 blocked。其餘檔案 Gate 1 pass：無超寬行、無未使用 import、無 debug 殘留、無註解掉的程式碼。
- Gate 2 在 `scripts/agent_skill_format/schema.py`、`scripts/validate_skills.py`、`scripts/tests/test_validate_skills.py` 失敗，這三個檔的 Gates 3-7 blocked。
- Gates 3、4 對其餘 gate-reviewed 檔案開啟並通過：`undeclared_directories` 的列目錄失敗經 `fail()` 報出並回傳失敗、訊息可行動（`agents/ is not declared under resources`）；無吞錯、無未終止迴圈、巢狀深度未超過 2。
- Gate 5 在 `scripts/agent_skill_format/read_whole.py` 與 `scripts/shell_script.py` 失敗，這兩個檔的 Gates 6-7 blocked。
- Gate 6 判準來源為 `AGENTS.md`、`PROJECT.md`、`docs/guards.md`、`skills/triage-findings/SKILL.md`（皆在樹內，非推定）；對仍在階梯上的檔案通過。與 spec 的對照本身由 Against-Contract 承載。
- Gate 7 在 `scripts/tests/test_module_claims.py` 失敗。
- Gate 8 未開啟，理由見 Calibration。

**未列為 finding 的觀察（Gate 1）**：`scripts/validate_skills.py:43-63` 與 `scripts/tests/test_validate_skills.py:15-19` 的 import 區塊在本次改動後失去分組——唯一的 repo 內匯入 `from skill_model import FORNAX_FORMAT, listed` 被夾在 `agent_skill_format.*` 之間，`schema` 排在 `skill_interface` 之後。這正好抵銷 `c13678d` 自述的目的（「putting it behind an import is what makes a back-edge visible」）。不列為 finding，因為 `development-knowns.yaml` 的 `import-grouping-unchecked` 已以 `treatment: accept` 記錄此條件並判定其缺陷為 cosmetic，而 `ruff.toml` 明文記載本 repo 未採納 import sorting；AGENTS.md 的權衡條款說每輪重報一次已受理的 debt「costs a finding and repairs nothing」。

### Against-Contract

| # | Clause | Falsifier attempted | Result | Evidence |
|---|---|---|---|---|
| 1 | AGENTS.md Script And Dependency Policy：「When a module takes ownership of a behaviour, enumerate every existing implementation of it.」 | 掃遍 `*.py`/`*.js`/`tools/`/host manifests 的每一個 `a-z0-9` 文法，找出既未導向 owner、也未被列舉句記錄的 skill 名稱拼法 | holds | `scripts/skill_model.py:39-46` 的列舉現已涵蓋 `development_knowns.ID`（`scripts/development_knowns.py:33`）、`skill_interface` 的 record pattern（`scripts/agent_skill_format/skill_interface.py:36`）、`seam_contract` 的 template marker（`scripts/seam_contract.py:55`）、`validate_skills` 的 `producer` group（`scripts/validate_skills.py:85`）、`handoff` 自己的 capture group（`scripts/skill_model.py:87`）。全樹掃描後無遺漏；`tools/`、`.claude-plugin/`、`.codex-plugin/`、`.opencode/` 無第二個拼法 |
| 2 | AGENTS.md Repository Hygiene：「Do not write a count of what the repository contains.」及其 transcription 推論 | 在新寫的 docstring 裡找對某棵樹的量測，並回頭檢查它是否由 commit message 轉錄而來 | **VIOLATED** | `scripts/validate_skills.py:360-365`。`aa93acd` 的 message 寫「run against the installed snapshot of tianheng-foundry **0.1.0**, it reports one undeclared adapter directory per skill, in every skill it ships」——帶版本釘選，屬 dated 量測；轉錄進 docstring 後版本被丟掉，成為「the other collection this format serves, **which ships** a per-skill host adapter directory **in every skill**」，一句對另一棵活樹的現在式全稱量測，該 collection 明天修掉就過期而無人察覺。同段「no skill in this repository **has ever** carried an undeclared directory, and **each one's** directories match its declared resources exactly」是對本樹的量測，用「each one / has ever」寫成不帶數字的總量，正是該條列舉的替代形式之一。兩者都該落在 dated record（`docs/guards.md` 或 `development-knowns.yaml`），不在 docstring |
| 3 | AGENTS.md Testing Strategy：「After repairing a defect, sweep the repository for the same class before calling it fixed. … by enumerating the mechanism」 | 列舉樹內每一處「哪些 Python 檔屬於 scripts/」的回答，看是否每處都對照了 package 搬移這個新性質 | **VIOLATED** | `c13678d` 明確修了 `scripts/tests/test_module_claims.py:31-35` 的 top-directory glob。同一機制在 `scripts/tests/test_check_workspace.py:40-46` 原封不動：`(check_workspace.ROOT / "scripts").glob("*.py")` 只掃頂層，用來找出所有含 `generated_block.dispatch` 的產生器。今天 package 內沒有產生器所以未失效，但這正是被修的那一類，而 sweep 是「enumerating the mechanism」而非「rereading the diff」——該處不在本 range 的 diff 內，所以只有 sweep 找得到它 |
| 4 | AGENTS.md Repository Hygiene：關於編輯已結算記錄的界線——「A row's label is not one of its readings, and may be corrected; an answer may not.」、「disclosed at the point of the edit」 | 對本 range 兩次編輯 `docs/dispositions/8dc34ca..ba81ab1.md` 的 Reach 座標，逐一問：改到的是 reading 還是 coordinate？是否在編輯處揭露？揭露是否可讀？ | **VIOLATED**（第二次） | 第一次（`266a703`）在界內：Reach cell 是 repair 要碰的座標，不是 verdict / count / reconciliation，且就地揭露。第二次（`1a84428`，三格 `skill_model.FormatSchema` → `schema.FormatSchema`）在實質上同樣在界內，但其揭露自我作廢：揭露句寫成「the three cells naming it as `schema.FormatSchema` now name it as `schema.FormatSchema`」——取代把揭露句自己的主詞也吃掉了，讀者再也無法從記錄裡得知改掉的是哪個名字。AGENTS.md 允許這類編輯的前提就是揭露；揭露失效，編輯就退回成未揭露的歷史改寫 |
| 5 | AGENTS.md Testing Strategy：「Read a dated evidence log by its headings」；`docs/guards.md`「A dated section is quotable only with the tree it names, so each one names its own.」 | 讀 `docs/guards.md` 新章節的標題，再讀它底下的列，問兩者是否一致 | **VIOLATED** | 標題為「## Written 2026-09-14, **prospective** — the ba81ab1 round, **nothing measured**」，而其下七列中有四列寫著 **measured** 與具體紅數。導言「**Four** can carry a guard once their repair lands. **The rest** are a module docstring's own claims about ownership」也被自己的表格推翻：被歸為「the rest」的 `DEFINITION-NAMED-ON-THE-BINDING` 那一列現在也是 **measured**。且該章節標題不含 commit（對照既有的 `Measured …, at <commit>` 寫法），所以四個量測沒有任何一棵樹可掛靠 |
| 6 | PROJECT.md：「`family` is a flat field …, the single source for README grouping and the generated skill maps」 | 以 `replace(FORNAX_FORMAT, families={"archaeology": …})` 跑 `validate_skills.main`，再跑 `skill_graph` | **VIOLATED**（已記錄的既決餘量，不計入 Findings） | `scripts/skill_graph.py:38,73,99` 仍讀 module binding，被釘在 `FORNAX_FORMAT` 上。與上一輪同一 falsifier、同一結果。差別在於本輪已把它明寫出來（`scripts/skill_model.py:20-27`），並在 `docs/guards.md` 記為「by decision rather than by omission」。故不作為新 finding 提出 |
| 7 | AGENTS.md Repository Hygiene：「Before adding a check, say what it would have caught and what it costs per change.」 | 對新增的 `undeclared_directories`，檢查是否交代了歷史失敗、是否到達使用者、以及每次改動的標準成本 | holds | `scripts/validate_skills.py:352-370` 與 `aa93acd` 的 message 兩處都交代。「到達使用者」那一半經本機安裝快照驗證為真（Claims Verified #9）。標準成本亦逐項命名。內容本身成立；它寫在哪裡的問題由第 2 列承載 |
| 8 | AGENTS.md Testing Strategy：「Check the fixture actually fails when the rule is removed」 | 找 `aa93acd` 對新檢查的突變量測紀錄 | unprovable statically | `aa93acd` 未記錄任何「removing the check turns N red」。同 range 其餘每一個帶 guard 的提交都寫了，本提交是唯一沒寫的。結構上 `test_a_directory_no_resource_key_names_is_refused` 在檢查被移除時必然轉紅；另一個新案 `test_the_folder_check_reads_shape_and_not_intent` 斷言的是 pass，移除檢查它仍綠，這一點提交自己說明了 |
| 9 | AGENTS.md Testing Strategy：hand-written matcher 需要兩個 negative control | 找本 range 新增、對某文法宣稱不變式的手寫 matcher | holds（空集合） | 新檢查 `undeclared_directories` 是集合成員判定，不是文法 matcher；它讀宣告路徑的第一段用的是 `PurePosixPath`，文法歸 `pathlib` 所有，符合「A matcher that reads a token must name the grammar's owner, and use it」 |
| 10 | AGENTS.md Repository Hygiene：「Do not cite a line number in durable prose.」 | 在本 range 新增的 docstring、註解、commit message、`docs/guards.md` 與 `docs/dispositions/` 的新文字中搜尋 `path:line` | holds | 全部只引符號與檔名。`docs/reviews/8dc34ca..ba81ab1.md` 大量使用 `path:line`，但 AGENTS.md 明言 Review Record 的 evidence 欄不在本條主體之內，且 `check_citations.RECORDS` 只涵蓋 `docs/dispositions`。相關的界線問題見 Structural Causes #6 |
| 11 | AGENTS.md Testing Strategy：「One commit per cause, not one per round.」 | 把六個已受理 cause 對到提交，看是否一一對應且無合併 | holds | cause 1 → `266a703`、cause 2 → `8b0c24c`、cause 3 → `b07e360`（3a/3b）與 `28d3c0f`（3c 的一半）、cause 4 → `9861912`、cause 5 → `3e02433`、cause 6 → `9a17615`。每個提交 message 都指名 cause 與 repair 編號 |
| 12 | AGENTS.md Final Report Notes：commit 不得含 AI 署名 | 檢查十一個提交的 trailers 與作者 | holds | trailers 全空，author 皆為 `tacticaldoll` |
| 13 | AGENTS.md Versioning / PROJECT.md「Release bumps are separate」 | 檢查是否動到 `distribution.json` 或 host manifest 版本 | holds | 四十五個檔案中無 `distribution.json`、無 host manifest |
| 14 | AGENTS.md Testing Strategy：「Persist the Review Record too … and name it from the Disposition Record's `Source`」 | 比對檔名與 Disposition Record 的 `Source` 欄 | holds | Source 為 `docs/reviews/8dc34ca..ba81ab1.md`，檔案存在且內容為該輪產出的原文 |
| 15 | AGENTS.md Language Policy | 檢查新增的中文檔案是否落在允許清單內 | holds | 中文只出現在 `docs/reviews/8dc34ca..ba81ab1.md`，正是條款點名的類別；同輪的 Disposition Record 為英文 |
| 16 | AGENTS.md Testing Strategy：「Derive the record's scope from the range」 | 以 `git diff --name-only 8dc34ca..ba81ab1` 對照 Disposition Record 的 Scope 欄 | holds | 實跑結果與記錄的 Scope 欄逐字相符 |

### Claims Verified

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | `c13678d`：「they are the set with **no edge out of it**」／`1a84428`：「the package **still imports nothing from this repository**.」 | `scripts/agent_skill_format/read_whole.py:28-29` 有 `if TYPE_CHECKING: import shell_script`，而 `scripts/shell_script.py` 留在 package 外；`read_whole.py:94` 的公開函式簽章 `shell_words(command: "shell_script.Line")` 直接以 package 外的型別為參數型別。反向邊同時存在：`scripts/shell_script.py:49` `from agent_skill_format.read_whole import Unread`。這是一條跨越該次改動所宣告邊界的**雙向循環** | **REFUTED**（與 Gate 5 #1 同一缺陷的「宣稱」軸，不重複計入 Findings） |
| 2 | `c13678d`：「Nothing else changes: no module is split, **no behaviour moves**.」 | `scripts/agent_skill_format/skill_interface.py:13-17` 的 Usage 區塊仍記載 `.venv/bin/python scripts/skill_interface.py …`，該路徑已不存在；而該模組是本 package 內唯一帶 `if __name__ == "__main__"` 的可執行 CLI | **REFUTED**（與 Gate 1 #1 同一缺陷的「宣稱」軸，不重複計入） |
| 3 | `docs/dispositions/8dc34ca..ba81ab1.md`：「The triage template asks for `file:line`；a Disposition Record is a record under this repository's citation rule …」 | `skills/triage-findings/SKILL.md:138-146` 寫的是「**Reach** — every location the repair touches, enumerated as **a file plus the unit inside it** … **Not `file:line`**」。該段在 `ba81ab1` 當時逐字相同。template 要求的正是該記錄實際採用的形式，根本不存在需要說明的偏離 | **REFUTED**（獨立缺陷；`6e90409` 的 subject 與整段 body 皆建立在此誤述之上） |
| 4 | 該記錄 Self-check：「pass — … **every Reach cell enumerates `file:line`**」 | 同一文件三行之前才說「The Reach column cites a symbol or a quoted phrase **rather than** `file:line`」；表格本身每一格都是符號或引述片語 | **REFUTED**（計入 Findings） |
| 5 | `docs/guards.md` 章節標題：「prospective — … **nothing measured**」 | 同章節四列寫 **measured** 並附紅數 | **REFUTED**（與 Against-Contract #5 同一缺陷，不重複計入） |
| 6 | `scripts/validate_skills.py:26-29`：「`main` … **It carries the only default**」 | `validate_skills.py:540` 的 `validate_skill` 同樣帶 `schema: FormatSchema = FORNAX_FORMAT`，其 docstring 也自承「The filling defaults **here** and nowhere below」。兩句在同一檔內互相牴觸。成因是 `b07e360` 移除 main 的參數後 `28d3c0f` 又加回，而只改了 module docstring | **REFUTED**（與 Gate 2 #2 同一缺陷，不重複計入） |
| 7 | `3e02433`：「Removing the proxy turns **2** red, measured.」 | 結構上為真，但第二紅是跨測試污染：unittest 於類別內以字串序執行，`test_the_family_mapping_cannot_be_written_under_either_name` 早於 `test_the_family_vocabulary_is_the_schema_s`。移除 proxy 後前者的寫入成功（紅 #1）並把 `"archaeology"` 真的寫進 `FORNAX_FORMAT.families`，後者因此失敗（紅 #2） | partial |
| 8 | `c13678d`：「Reverting that branch turns **7** red.」 | scope 內無執行證據；該分支若還原，`agent_skill_format.*` 會被當成第三方套件。目前帶該宣稱的模組共有十二個檔，而 subTest 失敗計數與模組數不必然相同 | unprovable statically |
| 9 | `aa93acd`：「run against the installed snapshot of tianheng-foundry 0.1.0, it reports one undeclared adapter directory per skill」 | 逐一比對：七個 skill 全部同時持有 `references/` 與 `agents/`，而 `skill.yaml` 的 `resources` 只宣告 `references/`。每個 skill 恰有一個未宣告目錄 | verified |
| 10 | `aa93acd`：「no skill in this repository has ever carried an undeclared directory」 | 對 `skills/` 二十二個 skill 逐一比對，全部相符；`templates/skill` 宣告三者且三者皆存在。新檢查在本樹上為零誤報 | verified（就當前樹而言；「has ever」的歷史半句 scope 內不可判定） |
| 11 | `28d3c0f`：「`NAME_PATTERN` has no code reader left」 | 全樹 grep：僅出現在繫結本身、`AGENTS.md`、`scripts/evidence_currency.py:185`、`scripts/agent_skill_format/schema.py:28` 四處，全為散文引用 | verified |
| 12 | `9a17615`：「The round's Reach for this cause enumerated three sites and the suite held four」 | Disposition 的 6a Reach 列三個；本提交實際轉換四個。主動揭露而非吸收 | verified |
| 13 | `c13678d`：「**Ten** modules … move into `agent_skill_format`」 | `git show --stat` 的 rename 條目恰為十個。屬 commit prose 中「這個 commit 做了什麼」的計數，為 count 規則明文除外 | verified |
| 14 | `c13678d`：「Citations are unaffected: the citation gate walks the scripts tree rather than its top directory」 | `scripts/check_citations.py:155` 使用 `scripts.rglob("*.py")`；搬移後名稱仍可解析 | verified |
| 15 | `aa93acd`：「Two existing cases created a references directory without declaring it and now declare it through one shared constant.」 | 新增 `MANIFEST_WITH_REFERENCES`，由兩個連結測試共用 | verified |
| 16 | `9a17615`：「Two sites deliberately keep a binding and are not converted」 | mapping-proxy case 讀 binding（該案宣稱就是兩者同一物件），`test_skill_graph` 讀 binding（`skill_graph` 自己讀它）。兩處理由與程式一致 | verified |
| 17 | `1a84428`：「The type's new module is named for what it holds rather than for the collection that fills it」 | module docstring 與欄位一致：型別本身不含任何值。但型別的 docstring 仍描述某個值的性質，見 Gate 2 #1 | partial |

### Structural Causes

| # | Finding | Cause (the thing to change) | Cause location | Gate that would carry it |
|---|---|---|---|---|
| 1 | Gate 1 #1、Claims Verified #2 | 把 Usage 區塊改成搬移後可執行的形式（`python -m agent_skill_format.skill_interface`，並註明路徑條件），或把入口留在 `scripts/` 的薄 wrapper 上——搬移一個帶 `__main__` 的模組時，它自己的呼叫方式是 reach 的一部分 | `scripts/agent_skill_format/skill_interface.py:13-17` | Gate 1 (fail) |
| 2 | Against-Contract #5、Claims Verified #5 | 把章節標題改寫為量測章節的既有形式並命名量測所依的那棵樹；或把已量測的列移出 prospective 章節。同時修正導言的分類 | `docs/guards.md:497-499` | Gate 2 (blocked) |
| 3 | Against-Contract #4、Claims Verified #3、#4 | 揭露段與 Self-check 列要跟著改：揭露句必須寫出被取代掉的舊名，Self-check 答案要改成該表實際採用的形式，「The triage template asks for `file:line`」整句應刪——template 要求的就是這個記錄在做的事 | `docs/dispositions/8dc34ca..ba81ab1.md:43-45`、`:53-55`、`:109` | Gate 2 / Gate 6 |
| 4 | — | guards 的「turns 2 red」其第二紅來自跨測試狀態污染而非 guard 本身。改任一測試方法名、或單獨以 `-k` 跑該案，記錄下來的數字就不成立。改法：註明第二紅是污染效應，或讓該案在 `addCleanup` 中還原 `FORNAX_FORMAT` | `scripts/tests/test_validate_skills.py:1868-1878` 對照 `docs/guards.md:505` | Gate 7 (blocked) |
| 5 | — | `FormatSchema` 的欄位型別是 `Mapping[str, str]`，型別本身不保證 proxy：`replace(FORNAX_FORMAT, families={...})` 在本 range 內就出現三次，產出的 schema 其 `families` 是普通 dict。5a 只修好了 `FORNAX_FORMAT` 這一個值。改法：在 `__post_init__` 中包裝，使 proxy 成為型別的性質 | `scripts/agent_skill_format/schema.py:22-25`、`:44` | Gate 2 (fail) |
| 6 | — | AGENTS.md 的引用豁免只點名「a Review Record's own **evidence column**」，但該記錄的座標分佈在四個欄位。豁免的措辭比它要豁免的物件窄。目前無實害，因為 `check_citations.RECORDS` 只走 `docs/dispositions`；一旦有人把 `docs/reviews` 加進去就會判錯 | `AGENTS.md` 該句、`scripts/check_citations.py:33-38` | Gate 6 |
| 7 | Gate 5 #1 | 三選一：(a) 把 `shell_script` 一併移進 package；(b) 讓 `read_whole.shell_words` 改收 package 內定義的型別，由呼叫端轉換；(c) 把 `shell_words` 移出 package。在三者之一落地之前，兩句宣稱必須改寫成實況 | `scripts/agent_skill_format/read_whole.py:28-29,94`、`scripts/shell_script.py:49` | Gate 5 (fail) |
| 8 | Gate 7 #1 | `test_module_claims.MODULES` 用 `{path.stem: path}` 回答「哪個檔是模組 X」，而同一問題在 `check_citations.modules` 早已有 owner，且該處 docstring 明文記載這個形狀曾經「answered the wrong question silently」。改法：改走 `check_citations.modules`，或至少複製 `collisions` 與回報行為；並把 `test_check_workspace` 的頂層 glob 一併納入同一次 sweep | `scripts/tests/test_module_claims.py:31-35` 對照 `scripts/check_citations.py:129-137,144-160`、`scripts/tests/test_check_workspace.py:40-46` | Gate 7 (fail) |

第 4、5、6 列是 Phase 3 結構萃取階段即已到手的讀數；階梯在對應檔案上關閉對應 gate，不代表這些成因要被扣住不說。

### Responsibility & Dependency Ledger

Gate 5 對下列 unit 開啟。未開啟的 in-scope unit 與各自原因：`validate_skills` 的四個 unit、`schema.FormatSchema`、`test_validate_skills.SchemaSeamTests` —— 皆為該檔 Gate 2 關閉階梯所致；`skill_interface` 的 Usage 區塊 —— 該檔 Gate 1 關閉階梯所致；三十三個僅有 import 重寫的檔案內的所有 unit —— Phase 3 覆蓋集合 `triage-only`；`unread` 為空。

| # | Unit | Its job (one clause) | Handed in | Reached directly |
|---|---|---|---|---|
| 1 | `read_whole.shell_words` | 把一條 shell 指令拆成詞，或回報讀不動 | `command`（型別為 package 外的 `shell_script.Line`） | `shlex`、`shell_script`（跨 package 邊界的型別相依） |
| 2 | `scripts/shell_script.py`（模組層） | 說一段 shell script 的指令在哪裡結束，或拒絕整段 | none | `agent_skill_format.read_whole.Unread`（跨邊界回指，與 #1 成環） |
| 3 | `distribution_manifest.validate_distribution` | 驗證正規 distribution metadata 與 host 投影 | `root`、`schema`（無預設） | `diagnostic_text.printable`、`read_whole.whole`、`workspace_files.listed`、檔案系統 |
| 4 | `scripts/skill_model.py`（模組層） | 宣告 Fornax 對 `FormatSchema` 的填充值 | none | `agent_skill_format.schema.FormatSchema`（單向，方向正確） |
| 5 | `agent_skill_format/__init__.py` | 宣告 package 的邊界前提 | none | none |
| 6 | `test_module_claims.imports` | 讀出一個模組匯入的名字，並把 package 匯入讀成它指名的那個模組 | `module` | `MODULES`、檔案系統 |
| 7 | `test_module_claims.third_party` | 遞迴列出一個模組觸及的已安裝套件 | `module`、`seen` | `LOCAL`、`STDLIB` |
| 8 | `test_module_claims.MODULES` | 列出每一個可被宣稱的模組 | none | 檔案系統（兩個 glob） |

Rows in this section are not findings.

### Gate 1: Formatting & Syntax Hygiene

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | `scripts/agent_skill_format/skill_interface.py:13-17` | Gate 1：模組搬移後留下的殘跡。Usage 區塊仍記載 `.venv/bin/python scripts/skill_interface.py …` 等三行，而該路徑已被同一提交刪除。這是 package 內唯一帶 `if __name__ == "__main__"` 的可執行入口，且改走新路徑直接執行也會在匯入時 ImportError。`c13678d` 的「no behaviour moves」對這個檔不成立 | 三行改為 `-m agent_skill_format.skill_interface` 形式並註明路徑條件；或在 `scripts/` 留一個薄 wrapper 以維持原命令 |
| 2 | `docs/guards.md:509` | Gate 1：全樹唯一一行行尾空白，且為本 range 新增。`ruff.toml` 選了 `W`，但 ruff 只讀 `.py`；`check_text._hygiene` 只查 NUL 與結尾換行，所以沒有任何 gate 會報它 | 刪去該列結尾的空白字元 |

### Gate 2: Naming & Readability

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | `scripts/agent_skill_format/schema.py:22-28` | Gate 2：型別的 docstring 描述的是某個**值**的性質。「the family mapping is proxied」「the module binding names the same object」——`FormatSchema` 既不 proxy 任何東西，也不知道有 module binding 存在。「The literals this gathers」也與 module docstring 的「knows the names of the fields and none of their values」牴觸。讀者照字面會以為拿到 `FormatSchema` 就拿到不可寫的 mapping；本 range 自己就有三處 `replace(FORNAX_FORMAT, families={...})` 的反例 | （a）在 `FormatSchema` 加 `__post_init__` 包成 `MappingProxyType`，使 docstring 對得上；或（b）把描述值的三句移回 `FORNAX_FORMAT` 宣告處 |
| 2 | `scripts/validate_skills.py:26-29` | Gate 2：同一檔內兩句互斥。module docstring 寫「`main` … It carries the only default」，而 `validate_skill` 同樣帶 default，其 docstring 也自承「The filling defaults here and nowhere below」。成因是 `b07e360` 移除 main 的參數後 `28d3c0f` 又加回，而只改了 module docstring。這是上一輪 Pattern 欄命名的同一形狀：值搬了，句子留在原地 | module docstring 改為兩處各持一個 default；或移除 `validate_skill` 的 default，使「the only default」成真 |
| 3 | `scripts/tests/test_validate_skills.py:1752-1763` | Gate 2：類別的契約句對多數成員不成立。`SchemaSeamTests` 說「Each case keeps one input fixed and changes only the schema」，但本 range 加入的五個案中只有一個改換 schema，其中一個斷言的還是 pass。類別名亦已與內容脫節：目錄檢查不是 schema seam | 把不換 schema 的案移到貼切的類別；或改寫 docstring 並改一個涵蓋得住的類別名 |

### Gate 5: Responsibility & Boundaries

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | `scripts/agent_skill_format/read_whole.py:28-29,94` 與 `scripts/shell_script.py:49` | Gate 5：依賴方向跨越了本次改動自己宣告的邊界，且成環。package 的公開函式 `read_whole.shell_words` 的參數型別是 `shell_script.Line`，`shell_script` 留在 repo 一側；`shell_script` 又反過來匯入 `read_whole.Unread`。`c13678d` 的選取判準與 `1a84428` 的宣稱都被這條邊推翻。`TYPE_CHECKING` 讓 runtime 不受影響，但 carve-out 的整個意義就是型別與 API 的可分離性。現有檢查抓不到它——`test_module_claims` 只問第三方，不問 repo 內的反向邊，所以「零反向相依」這個宣稱沒有任何守衛 | 三選一（Structural Causes #7）。在任一者落地之前，兩句宣稱改寫為實況。另建議把「package 內不得匯入 package 外模組」做成 `test_module_claims` 的第二個斷言——該檔已有 `imports()` 與 `LOCAL`，代價是幾行 |

### Gate 7: Deduplication & Composition

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | `scripts/tests/test_module_claims.py:31-35` | Gate 7：同一個問題在同一棵樹裡第三次被自己回答，而新的這份是靜默有損的。「哪個檔是模組 X」已有 owner：`check_citations.modules`，它回傳 `by_stem` 與 `collisions` 兩欄，其 docstring 逐字記載這個缺陷：「A dict keyed by stem answered the wrong question silently」。本次新增的 `MODULES` 正是那個被記錄過的形狀：同名時頂層檔勝出，package 內同名模組連同它的宣稱一起消失，且無任何訊號。第三份是 `test_check_workspace.py:40-46` 的頂層 glob——正是本 range 剛修過的那一類 | 改讀 `check_citations.modules`，或至少複製 `collisions` 並斷言為空；同一次改動把 `test_check_workspace` 的 glob 改成同一個 owner |

### Structural Appendix

**`agent_skill_format` package** — 十二個模組。宣稱前提「everything here answers a question about a published artifact … nothing here knows what Fornax decides」在 `read_whole.shell_words` 上不成立：它的參數型別屬於 package 外的 `shell_script`。package 對 repo 的唯一正向相依是 `skill_model → schema`，方向正確。

**`schema.FormatSchema`** — frozen dataclass，十個欄位，無方法、無行為、無 I/O、巢狀深度 0。`families` 的型別已由 `dict` 改為 `Mapping`，但型別層不強制 proxy：`replace()` 產出的 schema 其 mapping 可寫。docstring 描述的是 `FORNAX_FORMAT` 的性質而非型別的性質。

**`skill_model.FORNAX_FORMAT`** — 單一模組層級值，含兩個 `re.compile` 與一個 `MappingProxyType`。三個 binding 與它共用物件身分。`STATUSES` 已刪除。`NAME_PATTERN` 無程式讀者，docstring 現已指名它靠哪一種讀者留存。

**`validate_skills.undeclared_directories`** — 新檢查。只讀 skill 資料夾的**直接**子目錄，巢狀一層以下的未宣告目錄不在其內——這個界線 docstring 有寫。列目錄失敗以 `fail()` 回報而非讓 `OSError` 逸出。`declared_roots` 於路徑驗證**之前**累積，故一個非法宣告路徑仍會貢獻一個 root，但該路徑本身已另行判失敗，不構成漏放。

**`validate_skills.main`** — `schema` 參數在 `b07e360` 被移除、在 `28d3c0f` 帶著讀者回來。`parse_args` 仍無對應旗標，故 CLI 仍不可達；唯一讀者是 `test_a_run_carries_one_filling_into_both_halves`。上一輪記下的型別張力（`refactor` vs `feat`）因此仍維持在 `refactor` 側。

**`test_validate_skills.SchemaSeamTests`** — 八個測試。真正「固定輸入、只換 schema」的有四個；另四個不換 schema。mapping-proxy 案在 proxy 被移除時會污染 `FORNAX_FORMAT.families` 並依字串序影響其後的案。schema 各欄位的 seam 覆蓋：四個有測試，六個無。

**`docs/dispositions/8dc34ca..ba81ab1.md`** — 本 range 新增後被兩度編輯，對象皆為 Reach 欄座標。就性質而言未越界；就形式而言第二次的揭露句被自己的取代動作吃掉主詞而失效。另有兩處與 template 的事實不符。
