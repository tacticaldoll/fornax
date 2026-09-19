# 第一輪評分標準（在看到任何結果之前寫定）

第二輪的判準在 `scoring-round2.md`，它把 PER-UNIT 的 unit 清單從四個放寬到五個（加入 `InvoiceFormatter.__init__`）。本檔的四-unit 判準只適用於第一輪的 control 與 treatment。

Fixture 的 4 個 unit：
  U1 charge_customer          — 有問題：多職責 + 直接抓 POOL/BILLING_TOKEN/requests
  U2 apply_discount           — 乾淨，無外部依賴
  U3 InvoiceFormatter.render  — 乾淨，locale 由建構子handed in
  U4 monthly_totals           — 乾淨，plan_lookup 由參數handed in

要測的失效（hardening.md 協定第 2 項的 control 必須展現它）：
  「Gate 5 由最便宜的證據作答 —— 掃一次 import 方向就給一個 gate 層級判決，
    而沒有任何 unit 被逐一打開」

主要指標 PER-UNIT：輸出是否為 4 個 unit 各自作答？
  PASS = 四個 unit 全部出現且各有自己的判斷
  PARTIAL = 只涵蓋有問題的 unit（通常只有 U1），乾淨的 unit 從未被打開
  FAIL = 只有一個 gate 層級判決，沒有 unit 層級作答

次要指標 ORIGIN：是否逐一 unit 指出依賴來源（handed in vs reached directly）？
  PASS = 至少 3 個 unit 有明確來源標註
  PARTIAL = 只有 U1 有
  FAIL = 完全沒有來源區分

第三指標 VARIANCE（協定第 5 項）：5 reps 的輸出形狀是否收斂？

判定規則：
  - control 若未展現失效（PER-UNIT 已是 PASS）→ 依協定第 2 項，這個 wording 沒有要修的東西，
    應該撤掉，而非宣稱它有效。
  - treatment 若未顯著優於 control → wording 未 binding，known 維持 unevidenced。
  - 協定第 4 項：每一份都要人工讀過，不可只用關鍵字比對。
