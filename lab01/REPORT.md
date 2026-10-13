## 学生信息

- **姓名：江佩泽**
- **学号：112404260102**
- **班级：数据1241班**
- **GitHub 用户名：jiangpeize**
- **仓库地址：https://github.com/jiangpeize/bigdata-collection-labs-112404260102**

# 任务 1：判断数据加载方式

## 1.1 Device：判断动态加载并找到 API

### 判断结果

- 页面：`/devices`
- 数据加载方式：` 动态加载`
- 判断依据：`源代码搜不到（0/0），Network 里找到了那个请求`

请用 1～2 句话说明：

1. 在“查看网页源代码”中是否能搜索到页面上的设备名称；
2. 在 Network 的 Fetch/XHR 中是否找到返回设备数据的请求。

### API 信息

- Request URL：https://115.159.159.82/api/devices
- Request Method：GET
- Query 参数：page、page_size

### 【截图 1】Device API 发现证据

![Device API 发现证据](images/01_device_api.png)


## 1.2 Company：判断静态加载
- 页面：`/companies`
- 数据加载方式：`静态加载 `
- 判断依据：`能搜索到页面中真实显示的企业名称`

请说明：使用“右键 → 查看网页源代码”后，是否能搜索到页面中真实显示的企业名称。

### 【截图 2】Company 静态加载证据

文件名：

```text
images/02_company_source.png
```

**截图内容必须是“查看网页源代码”页面，不是 Elements，也不是 Jupyter。**

截图中应能看清：

1. 浏览器正在显示 `/companies` 的网页源代码；
2. 使用 `Ctrl + F` 搜索一个页面中真实存在的企业名称；
3. 源代码中能看到该企业名称或对应企业记录。

插入：


![Company 静态加载证据](images/02_company_source.png)


---

# 任务 2：Device API 分页采集

## 2.1 API 分页结构

填写你实际从 JSON 中观察到的字段：

| 含义   | JSON 字段 |
| ---- | ------- |
| 当前页  |    page     |
| 每页条数 |    page_size     |
| 设备总数 |     total    |
| 设备列表 |    items     |

---

## 2.2 关键代码

只填写分页采集的核心部分，不要粘贴整个 Notebook。

```python
# 从第一页响应中读取分页信息
total = data["_______total_________"]
page_size = data["_____page_size___________"]

total_pages = _________(total + page_size - 1) // page_size_____________________________

devices = []

for page in range(1, total_pages + 1):
    r = requests.get(
        api_url,
        params={
            "____page____": page,
            "___page_size_____": page_size
        },
        timeout=10
    )

    page_data = r.json()
    page_items = page_data["______items__________"]
    ___________________devices.extend(page_items)_____________________________
```

---

## 2.3 采集结果

- 每页条数：50
- 设备总数：5000
- 程序计算得到的总页数：100
- 最终采集设备数：5000
- 唯一 `device_id` 数：5000

回答：

> 为什么总页数应由 API 返回的 `total` 和 `page_size` 计算，而不是直接在代码里写死？

答：数据量会变、写死会漏采或多采。

---

# 任务 3：Company HTML 解析

## 3.1 企业记录 Selector

- 企业记录 selector：`article.company-card`
- 第 1 页企业记录数：20

说明为什么选择这个 selector：

- 主要使用了 `id / class / data-* / 父子层级` 中的哪一种？
- 是否参考过浏览器 Copy selector 或 AI？
- 最终为什么采用现在这个写法？

答：1.主要使用了 class（company-card），另外用 data-* 属性（data-company-id）取企业编号，没有依赖父子层级。
2.参考过浏览器 Copy selector，但它给出的是一条带很多 nth-child(...) 的深层路径，很长。
3.最终选 article.company-card，因为它只有一层、语义明确，页面结构怎么变它都不容易失效；而那种深层路径只要中间少一个节点就整体抓不到了。

---

## 3.2 关键代码

只填写“记录定位 + 一条记录的关键字段”。

```python
cards = soup.select("______article.company-card__________________________")

card = cards[0]

company_id = _____card.get("data-company-id")_________________________________
name = _________card.select_one("h2 a").get_text(strip=True)___________________________________
status = ____________card.select_one(".badge").get_text(strip=True)______________________________
```

行业、区域、设备数量使用 `dt/dd` 结构后，请写出你最终如何得到：

```python
industry = _____details["所属行业"]___________________________________
zone = ____________details["所在区域"]________________________________
device_count = _________int(details["设备数量"].replace("台", "").strip())___________________________
```

---

## 3.3 字段来源说明

任选 **2 个字段**说明：

1. 字段：company_id 

   - 来自：` HTML 属性`
   - 使用的方法：`card.get("data-company-id")`

2. 字段：name

   - 来自：`文本 `
   - 使用的方法：`card.select_one("h2 a").get_text(strip=True)`

---

# 任务 4：Company “下一页”分页

## 4.1 下一页元素

- “下一页” selector：`nav.pagination a:last-of-type`
- 第 1 页 `href` 示例：`/companies?page=2`

### 【截图 3】Company “下一页”元素

插入：


![Company 下一页元素](images/03_company_next.png)


---

## 4.2 关键代码

```python
next_link = soup.select_one("_______nav.pagination a:last-of-type_____________________")

next_href = ____next_link.get("href")____________________________________

next_url = urljoin(
    current_url,
    _____next_href___________________________________________
)
```

再用 2～3 句话说明：

> 你的程序如何完成“当前页 → 找下一页 href → 请求下一页 → 再解析”的循环？

答：程序用一个 for 循环重复 3 轮：每轮先 requests 请求 current_url，用 BeautifulSoup 解析出本页 20 条企业，再用选择器找到“下一页”链接并读出 href。因为 href 是相对路径，用 urljoin(current_url, next_href) 拼成完整地址，再赋值给 current_url。下一轮循环就请求这个新地址，如此一页页往下走，直到采满 3 页。

---

## 4.3 三页采集结果

| 页码     | 企业数 |
| ------ | ---:|
| 1      |   20  |
| 2      |   20  |
| 3      |   20  |
| **合计** |  60   |

- 唯一 `company_id` 数：60

---

# 任务 5：结果验证

## 5.1 最终结果

| 检查项                   | 结果  |
| --------------------- | ---:|
| Company 总数            |  60   |
| 唯一 `company_id`       |  60   |
| Device 总数             |  5000   |
| 唯一 `device_id`        |  5000   |
| Company–Device 不一致企业数 |  0   |

### 【截图 4】最终验证结果

插入：

![最终验证结果](images/04_validation.png)


---

## 5.2 一致性检查关键代码

只填写最关键的比较逻辑：

```python
from collections import Counter

device_counts = Counter(
    x["company_id"] for x in devices
)

mismatch_count = 0

for company in companies:
    cid = ________company["company_id"]__________________________________
    expected = __________company["device_count"]___________________________
    actual = __________device_counts.get(cid, 0)_____________________________

    if ________expected != actual:_____________________________________:
        mismatch_count += 1
```

回答：

> 为什么 `status_code == 200` 仍然不能说明“数据已经采集正确”？

答：200 只表示服务器成功返回了一个响应，但不保证返回的内容就是我们要的数据。
比如：请求的参数写错时，有些接口也会返回 200，但 body 里可能是空的列表或错误提示；
返回的 JSON 结构可能变了；或者只返回了第一页而没采到全部数据。
所以拿到 200 之后，还要检查 JSON 里的字段（如 total、items）是否正确、
数量是否符合预期，才能说数据采集正确。


---

# 任务 6：保存采集结果

确认已经生成：

```text
data/companies.json
data/devices.json
```

填写：

- `companies.json`：`已生成`
- `devices.json`：`已生成`

不需要截图 JSON 全文，也不需要把 JSON 内容复制到报告。

---

# 实验结论

答：通过本次实验我掌握了两种数据采集方式。静态加载页面（/companies）
数据直接写在 HTML 源码里，用 requests 拿到页面后用 BeautifulSoup
解析节点即可；动态加载页面（/devices）的数据在 HTML 源码里搜不到，
需要通过 F12 抓包找到背后的 API 接口，再直接请求 JSON 数据。
分页方式也不同：HTML 页面要解析"下一页"链接的 href 逐页翻页，
API 分页只需修改 page 参数循环请求，直到取够 total 条。
验证方面：我检查了记录总数和 id 的唯一性，并用 company_id 把
两份数据关联比对设备数量，60 家企业全部一致，确认采集结果正确。
