# 評分標準（在看到任何結果之前寫定）

## fixture 的埋設

宣稱（同一個改動講了三次）：
  commit message「Both new checks derive what they inspect from the workspace rather than
                  from a list kept beside them」
  docstring     「Both checks below derive their inputs from the workspace rather than from a
                  maintained list」
  AGENTS.md     「Every surface that carries the release version is discovered from the workspace,
                  so none of them depends on a maintainer remembering to register it」

反例（就在旁邊）：
  NOTICE_FILES 是硬寫的三元素 tuple，check_notice_banners 逐一走訪它
  → 第二個 check 正是那條原則的反例，而且是同一個作者在同一個改動裡寫的

雜訊（不是主要指標，但可被合理報出）：
  check_notice_banners 對不存在的檔案 silently continue

## 主要指標 SELF-CLAUSE

輸出是否把「從 workspace 推導、不用維護清單」列為一個**契約條款**，
並用 NOTICE_FILES 當作 falsifier 打破它？

  PASS    = Contract inventory 或 Against-Contract 出現該原則為一列，
            且結果為 VIOLATED（或等義），evidence 指向 NOTICE_FILES
  PARTIAL = 有提到 NOTICE_FILES 是硬編清單（例如當成一般 finding），
            但沒有把它連回改動自己宣告的原則
  FAIL    = 完全沒提，或只當成風格偏好

## 次要指標

INVENTORY-SHAPE  Contract inventory 是否明確納入「改動自己引入的原則」
NOISE            是否也報了 silently continue（兩組都可能報，不作為判準）

## 事先寫定的結論對應

  control PASS 率高（≥3/5） → 現行措辭已足夠，這個改動不必要，應撤回
  treatment 明顯高於 control → 措辭有效
  兩組都低                   → 措辭不足，需要更強的形式（例如寫進 Phase 4b 而非 Phase 3）
  兩組都高                   → 同第一項，撤回

協定第 4 項：每份人工讀，不可只用關鍵字比對。
