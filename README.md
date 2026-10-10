# 大数据采集与处理实验

- 姓名：江佩泽
- 学号：112404260102
- 班级：数据1241班

## 目录结构

```text
bigdata-collection-labs-112404260102/
├── README.md
└── lab01/
    ├── lab1_html_api.ipynb      # 实验一完整代码
    ├── REPORT.md                # 实验一报告
    ├── data/
    │   ├── companies.json       # 60 条企业记录
    │   └── devices.json         # 5000 条设备记录
    └── images/
        ├── 01_device_api.png
        ├── 02_company_source.png
        ├── 03_company_next.png
        └── 04_validation.png
```

## Lab 1 概要

| 数据源 | 加载方式 | 采集方式 | 结果 |
|---|---|---|---|
| `/devices` | 动态加载 | `GET /api/devices?page=N&page_size=50` | 5000 条，`device_id` 唯一 5000 |
| `/companies` | 静态加载 | `requests` + BeautifulSoup + 下一页 | 3 页 60 条，`company_id` 唯一 60 |

一致性检查：用设备表的 `company_id` 统计实际设备数，与企业页面的 `device_count` 比对，不一致企业数 = 0。
