# 第二輪人工評分（協定第 4 項：逐份閱讀）

## armB（修正措辭 + 表格）

rep 1  PER-UNIT 5/5 ✓  INFERRED ✓（明講 both were inferred）  MINIMAL ✓（拒開未使用成員 finding）
       額外：對 invoice 參數型別用了「not determinable from the reviewed scope」第三值
rep 3  PER-UNIT 5/5 ✓  INFERRED ✓  MINIMAL ✓（且明說 "none is claimed to be verified either"）
       額外：同樣用了第三值；並為 row 5 寫了「reached directly 但屬純邏輯，記錄非 finding」的判斷
rep 2  PER-UNIT 5/5 ✓  INFERRED ✓  MINIMAL ✓
       額外：自發指出「No structural extraction was supplied」並說明因此直接讀原始碼
rep 4  PER-UNIT 5/5 ✓  INFERRED ✓  MINIMAL ✓
       額外：把 inline 常數（rates 表、100 除數、"{:.2f}"）也列入 Reached directly；
             對 row/invoice 型別用第三值
rep 5  PER-UNIT 5/5 ✓  INFERRED ✓  MINIMAL ✓

### armB 小結（Q1 已回答）
PER-UNIT 5/5、INFERRED 5/5、MINIMAL 5/5 —— 與第一輪 treatment（舊措辭+表格）完全相同。
**修正後的措辭沒有破壞 binding。** 若有差別是往更細的方向：三份自發使用了
「not determinable from the reviewed scope」第三值，一份把 inline 常數也算成直接觸及。

## armC（修正措辭，**不給**表格規格）

rep 1  PER-UNIT 5/5 ✓「Five units are in scope; all five were opened. Each carries its two
       required clauses.」逐 unit 有 **Job:** 與 **Where each dependency comes from:**
       INFERRED ✓  MINIMAL ✓「I do not score them as unnecessary on scope alone」
rep 2  PER-UNIT 5/5 ✓「Units opened (5 of 5 in scope)」 INFERRED ✓ MINIMAL ✓「Recorded as unproven」
rep 3  PER-UNIT 5/5 ✓「All five callable units in scope were opened. Each gets its two required
       clauses.」 INFERRED ✓  MINIMAL ✓
rep 4  PER-UNIT 5/5 ✓「Every unit in scope was opened. Both required clauses are recorded for each.」
       INFERRED ✓  MINIMAL ✓「no minimality finding is recorded, and no minimality pass is claimed」
rep 5  PER-UNIT 5/5 ✓ 逐 unit 另外列出 I/O、captured deps、domain distribution
       INFERRED ✓  MINIMAL ✓「NOT JUDGED — the scope contains no evidence either way」

### armC 小結（Q2 已回答 —— 落在事先寫定的結論 (a)）

PER-UNIT 5/5、INFERRED 5/5、MINIMAL 5/5，**在完全沒有表格規格的情況下**。

→ **措辭本身 binding。表格是呈現形式，不是驅動力。**

形式 vs 內容的差別很清楚：
  armB 五份全是表格；armC 五份是逐 unit 的散文小節，格式各異
  但**內容完全收斂** —— 同樣的 5 個 unit、同樣的 job 判斷、同樣的依賴來源分類、
  同樣三個 unit 判 pass
表格帶來的是**格式收斂**；措辭帶來的是**實質**。

另外：多份 armC 自發輸出「no unit in scope is unopened」這類完備性陳述，
而它們從未看過要求這個的表格規格 —— 那是 gates.md 的
「Both clauses are this gate's required output for every unit it opened」在起作用。

## 三組對照總表

                      PER-UNIT  INFERRED  MINIMAL
control（舊措辭）        0/5       0/5      0/5
armB（新措辭+表格）      5/5       5/5      5/5
armC（新措辭，無表格）   5/5       5/5      5/5
