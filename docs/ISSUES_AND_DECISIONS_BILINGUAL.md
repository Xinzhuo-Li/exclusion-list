# Exclusion List ETL — Issues, Resolutions & Open Decisions
# 医疗 Exclusion List ETL — 问题、解决方案与待决策事项

**Project / 项目:** Six-State Medical Exclusion List Merge (MD, MA, MI, MS, MT, NE)  
**六州医疗 Exclusion List 合并（MD, MA, MI, MS, MT, NE）**

**Status / 状态:** Data cleaning complete; awaiting leadership decisions before national merge  
**数据清洗已完成；全国合并前待领导决策**

**Cleaned records / 清洗后记录总数:** 8,575

---

## Part 1 — Issues Identified and Resolved
## 第一部分 — 已识别并解决的问题

### 1. Michigan: Incorrect Dual Sanction Date Mapping
### 1. Michigan（密歇根州）：双制裁日期映射错误

| | |
|---|---|
| **EN** | Michigan source rows contain two sanction date columns (`Sanction Date1`, `Sanction Date2`). Initially, `Sanction Date2` was mapped to `REINDATE` (reinstatement date). This was semantically incorrect — `Sanction Date2` represents a **second sanction event**, not a reinstatement. |
| **中文** | Michigan 源数据包含两个制裁日期列（`Sanction Date1`、`Sanction Date2`）。最初将 `Sanction Date2` 映射到了 `REINDATE`（恢复纳入医保日期）。这在业务语义上是错误的——`Sanction Date2` 代表的是**第二次制裁事件**，而非恢复日期。 |

| | |
|---|---|
| **EN — Resolution** | Each parsed sanction date now generates a **separate exclusion record** with its own `EXCLDATE` and `EXCLTYPE`. `REINDATE` is left empty. A dedicated parser (`michigan_dates.py`) handles compound date strings (e.g. `2/14/18 6/14/18`). Result: 3,982 source rows → 4,921 cleaned records. |
| **中文 — 解决方案** | 每个解析出的制裁日期现在生成**一条独立的 exclusion 记录**，各有自己的 `EXCLDATE` 和 `EXCLTYPE`，`REINDATE` 置空。并新增专用解析模块（`michigan_dates.py`）处理复合日期字符串（如 `2/14/18 6/14/18`）。结果：3,982 行源数据 → 4,921 条清洗记录。 |

---

### 2. Mississippi: Indefinite Exclusion End Date Should Be Empty
### 2. Mississippi（密西西比州）：无限期 exclusion 结束日期应置空

| | |
|---|---|
| **EN** | Mississippi uses `Termination End Date = 2999-12-31` (Excel serial `401768`) and `Exclusion Period` ending in **"Indefinite"** to indicate exclusions with no fixed end. These were incorrectly converted to `REINDATE = 29991231`, implying a reinstatement date in year 2999. |
| **中文** | Mississippi 使用 `Termination End Date = 2999-12-31`（Excel 序列号 `401768`）及以 **"Indefinite"** 结尾的 `Exclusion Period` 来表示无固定结束日的排除。此前被错误转换为 `REINDATE = 29991231`，相当于在 2999 年有一个恢复日期。 |

| | |
|---|---|
| **EN — Resolution** | Records with indefinite exclusion period → `REINDATE` set to **empty**. Only records with a real bounded end (e.g. `October 30, 2002 – November 19, 2028`) retain a populated `REINDATE` (1 record). Previously affected: 192 records; now: 0 incorrect `REINDATE` values. |
| **中文 — 解决方案** | 无限期排除的记录 → `REINDATE` **置空**。仅有明确结束期的记录（如 `October 30, 2002 – November 19, 2028`）保留 `REINDATE`（共 1 条）。此前受影响 192 条；现已修正为 0 条错误的 `REINDATE`。 |

---

## Part 2 — Open Issues Requiring Leadership Decision
## 第二部分 — 待领导决策的遗留问题

### Issue 1: Full Names Not Truncated — PostgreSQL Fields Changed to TEXT
### 问题 1：全名不截断 — PostgreSQL 字段改为 TEXT

| | |
|---|---|
| **EN — Current approach** | Per business requirement, organization names and provider names are preserved in full. PostgreSQL columns (`busname`, `general`, `lastname`, etc.) use `TEXT` instead of OIG LEIE fixed-length limits (e.g. `BUSNAME` max 30 chars, `GENERAL` max 20 chars). |
| **中文 — 当前做法** | 按业务要求，机构名和 provider 姓名完整保留，不做截断。PostgreSQL 相应列（`busname`、`general`、`lastname` 等）使用 `TEXT` 类型，而非 OIG LEIE 固定长度限制（如 `BUSNAME` 最长 30 字符、`GENERAL` 最长 20 字符）。 |

| | |
|---|---|
| **EN — Scale** | 272 records have `busname` exceeding 30 characters. Longest observed: 115 characters. Example: `INFINITY INTEGRATED COUNSELING & HOLISTIC WELLNESS` (50 chars). |
| **中文 — 规模** | 共 272 条记录的 `busname` 超过 30 字符，最长 115 字符。示例：`INFINITY INTEGRATED COUNSELING & HOLISTIC WELLNESS`（50 字符）。 |

| | |
|---|---|
| **EN — Potential risk** | If the national `exclusion_main` table or downstream systems enforce strict OIG fixed-length fields, import may fail or values may be silently truncated. Data will not match the canonical CMS OIG LEIE file format. |
| **中文 — 潜在风险** | 若全国 `exclusion_main` 总表或下游系统强制要求 OIG 固定长度字段，导入可能失败或被静默截断，与 CMS OIG LEIE 标准文件格式不完全一致。 |

| | |
|---|---|
| **EN — Options for leadership** | **(A)** National table uses `TEXT` — no truncation at merge (recommended). **(B)** Keep full names in cleaned CSV; truncate only at merge into OIG-compliant main table, with a truncation log. **(C)** Confirm field definitions with Verbus before merge. |
| **中文 — 待领导选择** | **(A)** 全国总表统一使用 `TEXT`，合并时不截断（推荐）。**(B)** 清洗库保留全名，仅在合并入 OIG 合规总表时截断并记录日志。**(C)** 与 Verbus 确认全国表字段定义后再决定。 |

---

### Issue 2: Source Records Missing Effective Date (8 Records Total)
### 问题 2：源数据缺少生效日期（共 8 条）

#### 2a. Montana (MT) — 6 records

| | |
|---|---|
| **EN** | Six `a.k.a.` (alias) provider records in the Montana source file have **no Effective Date**. Names are now parsed correctly (e.g. `a.k.a. Saul Clement` → Last: Clement, First: Saul), but `EXCLDATE` cannot be populated from source. |
| **中文** | Montana 源文件中有 6 条 `a.k.a.`（别名）provider 记录**无 Effective Date**。姓名现已正确解析（如 `a.k.a. Saul Clement` → 姓 Clement，名 Saul），但 `EXCLDATE` 无法从源数据填充。 |

| | |
|---|---|
| **EN — Impact** | These records cannot be matched by exclusion date in claims screening. Matching by provider name remains possible. This is a **source data gap**, not a conversion error. |
| **中文 — 影响** | 这些记录无法通过排除日期在理赔筛查中命中，但仍可通过 provider 姓名匹配。属于**源数据缺失**，非转换错误。 |

#### 2b. Mississippi (MS) — 2 records

| | |
|---|---|
| **EN** | Two `Seyah Hospice Care` organization records in the Mississippi source Excel have a blank `Termination Effective Date` (`NaT`). A third related record for the same organization with date `2012-02-01` is correctly preserved. |
| **中文** | Mississippi 源 Excel 中两条 `Seyah Hospice Care` 机构记录的 `Termination Effective Date` 为空（`NaT`）。同机构另一条含日期 `2012-02-01` 的记录已正确保留。 |

| | |
|---|---|
| **EN — Impact** | Same as MT — date-based screening unavailable for these 2 records; name/NPI matching still possible. Source data limitation. |
| **中文 — 影响** | 与 MT 情况相同——这 2 条无法按日期筛查，仍可通过姓名/NPI 匹配。属源数据限制。 |

| | |
|---|---|
| **EN — Options for leadership** | **(A)** Retain records and add a `data_quality_flag = missing_excldate` field. **(B)** Exclude from main table until manually verified. **(C)** Contact state data source for correction. |
| **中文 — 待领导选择** | **(A)** 保留记录并增加 `data_quality_flag = missing_excldate` 标记。**(B)** 暂不导入总表，待人工核实。**(C)** 联系各州数据源请求补全。 |

---

### Issue 3: Sparse Fields in Source Data (Structural Limitation)
### 问题 3：源数据字段稀疏（结构性限制）

| State / 州 | Missing field / 缺失字段 | Extent / 比例 | Cause / 原因 |
|---|---|---|---|
| **Nebraska (NE)** | NPI | 82% (1,134 / 1,390) | PDF table does not include NPI for most providers |
| **Nebraska (NE)** | Address | 100% (1,390 / 1,390) | PDF table has no address column |
| **Massachusetts (MA)** | Address | 100% (294 / 294) | Source Excel has no address column |

| | |
|---|---|
| **EN** | These are inherent limitations of the state-published source files, not conversion errors. Claims matching for these states will rely primarily on NPI and/or provider name. |
| **中文** | 这些是州政府发布的源文件本身的局限，非转换错误。这些州的理赔匹配将主要依赖 NPI 和/或 provider 姓名。 |

---

### Issue 4: Cross-State Duplicate NPI — Retain Multiple Records or Deduplicate?
### 问题 4：跨州相同 NPI — 保留多条还是去重？

| | |
|---|---|
| **EN — Current state** | 15 NPIs appear in multiple `source_state` values. Example: NPI `1538334222` (Adam Medical Equipment) appears in **MD, MI, and NE** — likely the same organization listed independently by each state's Medicaid program. |
| **中文 — 现状** | 15 个 NPI 同时出现在多个 `source_state` 中。示例：NPI `1538334222`（Adam Medical Equipment）同时出现在 **MD、MI、NE** 三个州——很可能是同一机构被各州 Medicaid 项目独立收录。 |

| | |
|---|---|
| **EN — Options** | **(A) Retain all records** — each row keeps its `source_state`; supports audit trail and state-specific provenance (recommended). **(B) Cross-state deduplication** — keep one record per NPI in the national table; simpler but loses state-level sourcing. |
| **中文 — 选项** | **(A) 保留全部记录** — 每条保留其 `source_state`，便于审计溯源（推荐）。**(B) 跨州去重** — 全国总表每个 NPI 只保留一条；更简洁但丢失州级来源信息。 |

| | |
|---|---|
| **EN — Recommendation** | Retain multiple records at merge; use `source_state` to distinguish origin. Align rule with Verbus before inserting into national `exclusion_main`. |
| **中文 — 建议** | 合并时保留多条，以 `source_state` 区分来源；插入全国 `exclusion_main` 前与 Verbus 统一规则。 |

---

## Part 3 — Summary for Leadership
## 第三部分 — 领导汇报摘要

| Category / 类别 | EN | 中文 |
|---|---|---|
| **Resolved** | Michigan dual-date mapping fixed; MS indefinite REINDATE cleared; dedup logic redesigned; MD legend rows filtered; MT alias names parsed; EXCLTYPE exact-match fixed | Michigan 双日期映射已修正；MS 无限期 REINDATE 已置空；去重逻辑已重设计；MD 图例行已过滤；MT 别名姓名已修正；EXCLTYPE 精确匹配已修复 |
| **Data quality** | 6/6 states PASS validation; 0 high-risk conversion errors; 8,575 cleaned records | 六州校验全部 PASS；0 项高风险转换错误；共 8,575 条清洗记录 |
| **Needs decision** | Full-name TEXT vs OIG truncation; 8 missing-date records; cross-state NPI policy; national table schema with Verbus | 全名 TEXT vs OIG 截断；8 条无日期记录处理；跨州 NPI 策略；与 Verbus 确认全国表结构 |
| **Not yet done** | PostgreSQL import on server; merge into 50-state `exclusion_main` | PostgreSQL 服务器导入；合并入 50 州 `exclusion_main` 总表 |

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

*Document generated for team reporting. 本文档供团队汇报留存使用。*
