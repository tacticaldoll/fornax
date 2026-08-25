# 人工評分（協定第 4 項：每份都讀過，非關鍵字比對）

## 形狀差異（最顯著的發現）

control 是 **finding-shaped**：編號缺陷清單 5.1~5.7，unit 只以「缺陷的主詞」出現。
treatment 是 **ledger-shaped**：先一張表，每個 unit 一列（job / handed in / reached directly），然後才是 findings。

## PER-UNIT（每個 unit 是否各自作答：job 一句 + 依賴來源）

control  1  ✗  無任何 unit 有 job клause；來源僅 U1 明確、U4 順帶
control  2  ✗  同上；U4 的 plan_lookup 完全未提
control  3  ✗  有「Noted as correct」提到 monthly_totals 注入
control  4  ✗  有「Positive signal」提到 plan_lookup 是參數
control  5  ✗  無正面段落；U2/U3 僅出現在 module 層級 finding 裡
         → 0 / 5 產出逐 unit 作答

treatment 1  ✓  5 列完整表 + 「Units not opened: none」
treatment 2  ✓  5 列完整表 + 「All five in-scope units were opened」
treatment 3  ✓  5 列完整表 + 「Units not opened: none.」
treatment 4  ✓  5 列完整表 + 「Units in scope this gate did not open: none」
         → 4 / 4（第 5 個待回）

註：treatment 全部把 InvoiceFormatter.__init__ 與 .render 拆成兩個 unit（5 個而非我預設的 4），
    顆粒度比評分表預期更細。

## VARIANCE（協定第 5 項：收斂 = wording 有咬住）

control   發散：findings 數 6/6/6/7/7；三份自發加正面段落、兩份沒有；排序各異
treatment 高度收斂：四份表格結構相同、unit 切法相同、欄位語意相同，
          job 用字甚至逐字相同 —— 「format one invoice as a locale-tagged display string」
          在 T1/T2/T3/T4 一字不差

## 新措辭的其他條款是否也被執行（control 完全沒有）

- 「layering 未宣告時要說是 inferred」  → treatment 4/4 明講 inferred；control 0/5
- 「minimality 只對 scope 內 call site 判，未使用成員不因此算多餘」→ treatment 4/4 明確
  引用此規則並拒絕開 finding；control 0/5
- 「Rows in this section are not findings.」→ T1/T2/T3 逐字輸出（這正是 round 1 那個
  未被 emit 的宣告，5bb0f90 修的東西）

## ⚠ 必須誠實記錄的落差

gates.md 說失效是「由最便宜的證據作答，**reads as passed** while no unit was opened」。
control 5 份全部 FAIL 該 gate，且都做了實質分析 —— **沒有任何一份 "reads as passed"**。
實際重現的是較弱的版本：乾淨的 unit 從未被當作 unit 打開，其狀態未被陳述。

→ 措辭有效，但 gates.md 的那句理由**誇大了 control 的行為**。這是對 repo 自身散文的發現。

## 最終計分（10/10 全數回收，逐份人工閱讀）

               PER-UNIT 逐unit作答   「inferred」  minimality規則  「not findings」宣告
control  1-5        0 / 5              0 / 5         0 / 5            0 / 5
treatment 1-5       5 / 5              5 / 5         5 / 5            4 / 5

treatment rep 5 同樣輸出完整 5 列表、「All five in-scope units were opened」、
inferred layering、minimality 拒開 finding。
