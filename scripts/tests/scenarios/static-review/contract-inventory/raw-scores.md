# 第三輪人工評分（協定第 4 項）

## control（現行措辭）

rep 1  SELF-CLAUSE **PASS**
       C1「Both new checks derive what they inspect from the workspace rather than from a list
       kept beside them」列為條款，falsifier 直指 NOTICE_FILES，判 VIOLATED。
       另外自發寫出：「AGENTS.md ... is amended by this same commit to assert the property under
       review, so it is not an independent source of truth for this change — it is a clause to be
       falsified like the rest.」
       → 這正是 treatment 想加的行為，control 已經做到。
       K3 判 REFUTED，理由是「the exact mechanism the commit claims was eliminated」。

⚠ 立即浮現的效度疑慮（在其餘資料進來前記下，避免事後合理化）：
   fixture 把原則同時寫進 commit message、docstring **和 AGENTS.md**。
   AGENTS.md 是 governance doc，所以那條原則同時也是「改動所 touches 的 invariant」——
   落在現行措辭本來就涵蓋的範圍內。
   而我真實遇到的五個實例，只有一個是 AGENTS.md 散文；其餘在 commit message、
   docstring、code comment。
   → fixture 可能沒有分離出 introduces 與 touches 這個變因。

   但這是效度問題，不是結果。事先寫定的結論仍然適用：
   control PASS 率 ≥3/5 → 撤回。若要用更好的 fixture 重測，那是**新的一次測試**，
   要重新事先登記，不能拿舊測試的結論回頭改。

rep 2  SELF-CLAUSE **PASS**
       Against-Contract 第 1 列即為該原則，VIOLATED，evidence 指 NOTICE_FILES:12-16。
       Claims Verified #3「NOTICE_FILES is precisely a list kept beside the check」→ REFUTED。

## treatment（加了 introduces 條款）

rep 3  SELF-CLAUSE **PASS**
       明確引用新措辭：「The change **introduces** its governing principle in three places at once
       ... so that principle is a clause the rest of this same change must already satisfy.」
       K3:「The rule is stated three times in this change and broken by the second place it had
       to be applied」—— 新措辭的用語直接出現在輸出裡。

## 事先寫定的結論（原文，未經修改）

  control PASS 率高（≥3/5） → 現行措辭已足夠，這個改動不必要，應撤回

目前 control 2/2 PASS。若維持，結論就是撤回，不論 treatment 表現多好。

rep 4  SELF-CLAUSE **PASS** — C2 列為 invariant，第 2 列 VIOLATED，evidence NOTICE_FILES:12-16
       另外自發抓到「the change adds a second maintained registry while claiming registries are gone」
rep 5  SELF-CLAUSE **PASS** — C2 列為 invariant，第 2 列 VIOLATED
       另外自發抓到 HOST_VERSION_MANIFESTS 也是維護清單，同一個宣稱在既有程式碼裡也不成立

## ★ 決定性發現：我假設的缺口不存在

我的假設是 Phase 3 只涵蓋「touches」的 invariant，所以 commit message / docstring
裡新立的原則不會被盤點。**control 直接反證了這一點：**

  rep 2 明列「A3 (invariant) — 來自 commit message」「B2 (invariant) — 來自 module docstring」
  rep 5 明列「C2 ... 來自 commit message；restated at release_surfaces.py:3-4」
  rep 1 明列來源為「commit msg ¶2; scripts/release_surfaces.py:1-5」

現行 Phase 3 的「stated project invariants」本來就被讀得夠寬，涵蓋 commit message
與 docstring。**touches vs introduces 的區分在實務上不存在。**

## 結論（照事先寫定的標準執行）

control 4/4 PASS → **撤回 SKILL.md 的措辭改動。**
hardening.md 第 2 項：「If the control does not exhibit the failure, there is nothing to
fix — stop and drop the guidance.」

## 那我那五個缺陷是怎麼來的？

不是 skill 缺機制 —— 是**沒有人對我的改動跑 static-review**。
我做的是臨時的對抗性檢視，而 Phase 4b 這條軌道本來就會抓到它們。
真正缺的是「套用」，不是「措辭」。

rep 3 (control)  SELF-CLAUSE **PASS** —— 而且比多數 treatment 更深：
       它把 scripts/workspace_files.py:5-8 與 PROJECT.md:57-58 也列為
       「改動所 touches 的既有專案不變量」，並用它們當 falsifier
       （「the project already exposes workspace_files(root) for exactly this question」）。

## treatment 補完

rep 1  PASS —— 明確標註 C1/C6/C7 為「invariant introduced」，並寫
       「Their first counter-example sits beside them」
rep 2  PASS
rep 5  PASS —— 直接引用新措辭作為**搜尋啟發式**：
       「Per the skill's rule about a principle stated for the first time, its first
        counter-example is expected beside it: the second place the author had to apply it.
        That is check_notice_banners」

## 最終計分

                SELF-CLAUSE
control              5 / 5      ← 現行措辭
treatment            5 / 5      ← 加了 introduces 條款（rep 4 最後回來，同樣 PASS）

## 執行事先寫定的結論

control ≥3/5 → **撤回**。已於 2026-08-25 執行 git checkout。
hardening.md 第 2 項：control 未展現該失效，就沒有東西要修。

## 誠實的細緻差別（不足以推翻結論）

新措辭確實加了一個**搜尋啟發式** —— treatment rep 5 用它來預測該去哪裡找反例。
但 control 在沒有那個提示的情況下找到同一個東西，而且 rep 3 還找得更深。
啟發式讓路徑更短，不改變結果。事先寫定的標準沒有為「路徑更短」留位置，
而事後為它開一個位置，正好就是這個 session 反覆在防的那件事。

rep 4 (treatment)  SELF-CLAUSE **PASS** —— 第 2 列即為該原則，
       並寫「the rule's first counter-example sits beside the rule」

## 那五個真實缺陷的正確歸因

不是 skill 缺機制。是**沒有人對我的改動跑 static-review**。
Phase 3 + Phase 4b 本來就會抓到它們 —— control 五份都證明了。
缺的是套用，不是措辭。
