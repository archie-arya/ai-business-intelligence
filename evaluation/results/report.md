# BI Agent Evaluation Report

## Progress

- Completed: 21
- Failed: 2
- Total benchmark questions: 23

## Metrics

| Metric | Result |
|---|---:|
| Tool-selection exact match | 42.9% |
| Unnecessary tool-call rate | 6.2% |
| RAG source recall | 42.9% |
| RAG source precision | 13.1% |
| Deterministic answer match | 66.7% |
| Multi-source success | 66.7% |
| Mean latency | 94.25s |
| Median latency | 70.40s |
| P95 latency | 192.41s |

## Notes

The answer-match metric is only a deterministic
substring check. It is not an LLM-as-judge evaluation.

The benchmark is intentionally sequential because
the current agent uses local Ollama inference.

## Failed Questions

- **multi_001**: ValueError('PostgreSQL rejected the generated read-only query: relation "fact_sales_line" does not exist\nLINE 1: SELECT SUM(line_revenue) AS q4_revenue FROM fact_sales_line ...\n                                                    ^')\n- **multi_006**: ValueError('PostgreSQL rejected the generated read-only query: relation "fact_sales_line" does not exist\nLINE 1: ... quarter, SUM(line_revenue) AS total_revenue FROM fact_sales...\n                                                             ^')\n
## Slowest Questions

- **multi_005** — 282.92s — What were the quarterly sales results and what does a sales line represent?\n- **multi_003** — 206.86s — What were sales by quarter and how should returns affect revenue?\n- **multi_004** — 192.41s — What was revenue by quarter and what is the difference between gross and net revenue?\n- **sem_004** — 168.86s — Can a promotion increase volume while reducing realized revenue per unit?\n- **multi_007** — 137.73s — What were the quarterly sales results and what does an order represent?\n- **multi_008** — 134.74s — What was quarterly revenue and what policy should be used to interpret it?\n- **sem_003** — 111.68s — What happens to recognized sales when merchandise is returned?\n- **multi_002** — 98.28s — What was revenue by quarter, and what does the business mean by revenue?\n- **sem_002** — 81.70s — What inventory buffer protects us from forecast error?\n- **sem_007** — 75.05s — What measure tells us how efficiently inventory becomes sales?\n