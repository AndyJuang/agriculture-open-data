# 農業開放資料查詢 Skill

在 Codex 用中文查詢農業部開放資料。內建農糧署糧情調查（EIR837），可依年份、縣市、鄉鎮、期作及作物查詢並匯出 CSV。其他資料集會從官方目錄查找，再依各資料集的介接規格取數。

## 安裝與試用

在本機 Codex 開啟任一可寫入的工作資料夾，複製下方整段提示詞。查詢腳本使用 Python 3 標準函式庫，執行環境需要能連線至農業部 API。

### 1. 安裝技能

```text
請用 $skill-installer 從 https://github.com/AndyJuang/agriculture-open-data/tree/main/agriculture-open-data 安裝 agriculture-open-data 技能。
請安裝到我的個人技能目錄 ~/.agents/skills，讓不同專案都能使用。若同名技能已存在，先確認安裝位置並告訴我。安裝後請確認 SKILL.md、rice.md 和 scripts/fetch_rice.py 都存在，並回報技能路徑。
```

若安裝完成後技能未出現在選單，請重新啟動 Codex。參考 [OpenAI 的技能安裝與載入說明](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)。

### 2. 試查糧情並匯出

```text
請使用 $agriculture-open-data，查西元 2020 到 2024 年花蓮縣各鄉鎮一期作稉稻的收穫面積和稻穀總產量。把官方原始明細匯出成 CSV，並列出各年取得的筆數、資料來源及擷取日期。若有年度查無資料或連線失敗，請指出是哪一年及原因。
```

### 3. 探索其他農業資料

```text
請使用 $agriculture-open-data，從農業部官方資料目錄找 2024 年可用的番茄價格資料。列出候選資料集、價格口徑和可查期間，再試取臺北二市場 2024 年 11 月的批發行情。請保留官方品項名稱，並附上來源與實際涵蓋日期。
```

## 資料來源

- [農業部農業資料開放平臺](https://data.moa.gov.tw/)
- [糧情調查欄位與介接筆記](agriculture-open-data/rice.md)
