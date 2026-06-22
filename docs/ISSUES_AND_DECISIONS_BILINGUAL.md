# Exclusion List ETL — Issues, Resolutions & Decisions
# 医疗 Exclusion List ETL — 问题、解决方案与决策事项

**Project / 项目:** Six-State Medical Exclusion List Merge (MD, MA, MI, MS, MT, NE)  
**六州医疗 Exclusion List 合并（MD, MA, MI, MS, MT, NE）**

**Status / 状态:** Leadership decisions confirmed; PostgreSQL deployed; ready for six-state delivery  
**领导决策已确认；PostgreSQL 已部署；六州范围可交付**

**Cleaned records / 清洗后记录总数:** 8,575

---

## Part 1 — Issues Identified and Resolved
## 第一部分 — 已识别并解决的问题

### 1. Michigan: Incorrect Dual Sanction Date Mapping
### 1. Michigan（密歇根州）：双制裁日期映射错误

| | |
|---|---|
| **EN — Resolution** | Each parsed sanction date generates a **separate exclusion record** with its own `EXCLDATE` and `EXCLTYPE`. `REINDATE` is left empty. Result: 3,982 source rows → 4,921 cleaned records. |
| **中文 — 解决方案** | 每个解析出的制裁日期生成**一条独立的 exclusion 记录**，各有自己的 `EXCLDATE` 和 `EXCLTYPE`，`REINDATE` 置空。结果：3,982 行源数据 → 4,921 条清洗记录。 |

---

### 2. Mississippi: Indefinite Exclusion End Date Should Be Empty
### 2. Mississippi（密西西比州）：无限期 exclusion 结束日期应置空

| | |
|---|---|
| **EN — Resolution** | Records with indefinite exclusion period → `REINDATE` set to **empty**. Previously affected 192 records; now 0 incorrect `REINDATE` values. |
| **中文 — 解决方案** | 无限期排除的记录 → `REINDATE` **置空**。此前受影响 192 条；现已修正为 0 条错误的 `REINDATE`。 |

---

## Part 2 — Leadership Decisions (Confirmed)
## 第二部分 — 领导决策（已确认）

**Decision date / 决策日期:** 2026-06-20

### Decision 1: Retain Full Name Length (TEXT, No Truncation)
### 决策 1：保留全名长度（TEXT，不截断）

| | |
|---|---|
| **EN** | **Confirmed:** `exclusion_main` and `cleaned_staging` use `TEXT` for name fields. No OIG fixed-length truncation at merge. 272 records with `busname` > 30 chars are preserved in full. |
| **中文** | **已确认：** `exclusion_main` 与 `cleaned_staging` 姓名相关字段使用 `TEXT`，合并时不做 OIG 固定长度截断。272 条 `busname` 超过 30 字符的记录完整保留。 |

---

### Decision 2: Missing EXCLDATE = Long-Term Exclusion (Keep Empty)
### 决策 2：无 EXCLDATE 视为长期 exclusion（保留为空）

| | |
|---|---|
| **EN** | **Confirmed:** 8 records without `EXCLDATE` (MT 6 + MS 2) are **retained** in the main table. Empty `excldate` means long-term/indefinite exclusion per business rule. No placeholder date (e.g. `29991231`) is inserted. |
| **中文** | **已确认：** 8 条无 `EXCLDATE` 的记录（MT 6 + MS 2）**保留**在总表中。`excldate` 为空表示长期/无限期 exclusion，不填充占位日期。 |

---

### Decision 3: Cross-State Duplicate NPI — Retain All Records
### 决策 3：跨州重复 NPI — 保留全部记录

| | |
|---|---|
| **EN** | **Confirmed:** All 15 NPIs appearing in multiple `source_state` values are **retained** as separate rows. Each row keeps its `source_state` for audit and provenance. No cross-state deduplication. |
| **中文** | **已确认：** 15 个跨州重复 NPI **全部保留**为独立记录，每条保留其 `source_state`，不做跨州去重。 |

---

### Decision 4: exclusion_main Must Strictly Sync with cleaned_staging
### 决策 4：exclusion_main 必须与 cleaned_staging 严格同步

| | |
|---|---|
| **EN** | **Confirmed:** After merge, `exclusion_main` row count and all business columns must match `cleaned_staging` exactly for the six states. Merge uses DELETE-then-INSERT from `cleaned_staging`. Verification: `sql/04_verify_main_sync.sql`. |
| **中文** | **已确认：** 合并后 `exclusion_main` 行数及全部业务字段必须与 `cleaned_staging` 完全一致。合并方式为 DELETE 后从 `cleaned_staging` INSERT。验证脚本：`sql/04_verify_main_sync.sql`。 |

---

## Part 3 — Known Source Data Limitations (Not Conversion Errors)
## 第三部分 — 已知源数据局限（非转换错误）

| State / 州 | Missing field / 缺失字段 | Extent / 比例 | Cause / 原因 |
|---|---|---|---|
| **Nebraska (NE)** | NPI | 82% (1,134 / 1,390) | PDF table does not include NPI for most providers |
| **Nebraska (NE)** | Address | 100% (1,390 / 1,390) | PDF table has no address column |
| **Massachusetts (MA)** | Address | 100% (294 / 294) | Source Excel has no address column |

| | |
|---|---|
| **EN** | Claims matching for these states will rely primarily on NPI and/or provider name where available. |
| **中文** | 这些州的理赔匹配将主要依赖 NPI 和/或 provider 姓名（在源数据可用时）。 |

---

## Part 4 — Summary
## 第四部分 — 摘要

| Category / 类别 | EN | 中文 |
|---|---|---|
| **Resolved** | Michigan dual-date; MS indefinite REINDATE; dedup logic; MD legend filter; MT alias names; EXCLTYPE exact-match | Michigan 双日期；MS 无限期 REINDATE；去重逻辑；MD 图例过滤；MT 别名；EXCLTYPE 精确匹配 |
| **Decisions confirmed** | Full-name TEXT; empty EXCLDATE = long-term; retain cross-state NPI rows; strict main/staging sync | 全名 TEXT；空 EXCLDATE=长期；保留跨州 NPI；main 严格同步 staging |
| **Deployed** | PostgreSQL on vesta (port 5433); 6 stage tables + cleaned_staging + exclusion_main (8,575 rows) | PostgreSQL 已部署；6 张 stage 表 + cleaned_staging + exclusion_main（8,575 行） |
| **GitHub** | https://github.com/Xinzhuo-Li/medicaid-exclusion-list | 代码已上传 GitHub |

---

## Appendix — Record Counts by State
## 附录 — 各州记录数

| State | Source rows / 源文件行数 | Cleaned records / 清洗后记录 | Notes / 备注 |
|---|---|---|---|
| MD | 1,605 | 1,603 | 6 legend rows filtered / 过滤 6 条图例行 |
| MA | 294 | 294 | No address in source / 源文件无地址 |
| MI | 3,982 | 4,921 | Multi-date expansion / 多日期展开 |
| MS | 194 | 193 | 2 missing effective date in source / 源文件 2 条无生效日期 |
| MT | 174 | 174 | 6 alias records missing date in source / 6 条别名记录源文件无日期 |
| NE | 1,391 | 1,390 | 82% missing NPI; no address / 82% 无 NPI；无地址 |
| **Total** | **7,640** | **8,575** | |

---

*Document updated after leadership decisions. 本文档已于领导决策后更新。*
