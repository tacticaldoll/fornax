# 評分標準（在看到任何結果之前寫定）

沿用第一輪的 fixture；指標相同但 PER-UNIT 的 unit 清單放寬為 5 個（第一輪為四個，未計入 `InvoiceFormatter.__init__`）：
  U1 charge_customer / U2 apply_discount / U3 InvoiceFormatter.__init__
  U4 InvoiceFormatter.render / U5 monthly_totals

## 主要指標

PER-UNIT  每個 unit 各自作答（job 一句 + 依賴來源），全部 5 個
INFERRED  未宣告 layering 時明講 inferred
MINIMAL   interface minimality 只對 scope 內 call site 判，拒開未使用成員的 finding

## 對照基準（第一輪已測，control 不需重跑）

control（舊措辭）        PER-UNIT 0/5  INFERRED 0/5  MINIMAL 0/5
treatment（舊+表格）     PER-UNIT 5/5  INFERRED 5/5  MINIMAL 5/5

## 這輪要回答的兩個問題

Q1 修正後的措辭有沒有破壞 binding？
   armB 對照舊 treatment。若 armB 明顯低於 5/5 → 修正傷到了指引，要退回或重寫。

Q2 措辭本身能不能 binding，還是只是「給了表格就會填」？
   armC 是關鍵。三種可能結論，事先寫定：
     (a) armC PER-UNIT 高（≥4/5）→ 措辭本身 binding，表格是呈現形式而非驅動力
     (b) armC PER-UNIT 低（≤1/5）→ 是表格在驅動，措辭本身不足；
         則 known 不能關，且該考慮把 per-unit 要求寫進 gates.md 更強的形式
     (c) armC 中間（2-3/5）→ 兩者都有貢獻，收斂度會是判準；記錄為部分分離

## 不可事後調整

上面三種結論在看到資料前就寫定。協定第 4 項：每份人工讀，不可只用關鍵字比對。
