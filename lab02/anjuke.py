# -*- coding: utf-8 -*-
"""实验二 第二阶段：安居客教学站房源采集 → data/houseinfo.csv

8 个字段顺序：title → house → address → struct → area → floor → maketime → price
"""
import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
START_URL = "http://www.bspider.top/anjuke/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
FIELDS = ["title", "house", "address", "struct", "area", "floor", "maketime", "price"]
MAX_PAGES = 20          # 安全页数上限，防止无限循环
SLEEP_SECONDS = 1.2     # 每次请求之间至少停 1 秒


def get_text(node):
    """取节点完整文字；地址、户型由多个 span 拼成，不额外插入空格。"""
    return node.get_text("", strip=True) if node else ""


def parse_one(row):
    """解析一条房源：row 是 div.property 节点，返回按 8 个字段排好的列表。"""
    title = get_text(row.select_one("h3"))
    house = get_text(row.select_one("p.property-content-info-comm-name"))
    address = get_text(row.select_one("p.property-content-info-comm-address"))
    struct = get_text(row.select_one("p.property-content-info-attribute"))

    area = floor = maketime = ""
    # 属性组的顺序是：户型、面积、朝向、楼层、建造年代，但偶尔缺项，
    # 所以按内容判断，而不是死记下标，避免把“南北”当成楼层。
    for p in row.select("p.property-content-info-text"):
        text = get_text(p)
        if "室" in text and "厅" in text:      # 户型那一项，已单独取过
            continue
        if ("㎡" in text or "m²" in text) and not area:
            area = text
        elif "建造" in text and not maketime:
            maketime = text
        elif "层" in text and not floor:
            floor = text
        # 剩下的“南北”“东南”等朝向不要

    # 单价取每平方米均价，不要取 property-price-total（那是“148万”总价）
    price = get_text(row.select_one("p.property-price-average"))
    return [title, house, address, struct, area, floor, maketime, price]


def fetch_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.text, "html.parser")


def main():
    records = []
    visited = set()
    url = START_URL
    page_no = 0

    while url and url not in visited and page_no < MAX_PAGES:
        page_no += 1
        visited.add(url)
        soup = fetch_soup(url)

        rows = soup.select("div.property")
        if not rows:
            raise RuntimeError("第%d页没有解析到房源，请检查页面是否变成验证页" % page_no)
        page_records = [parse_one(r) for r in rows]
        records.extend(page_records)
        print("第%d页 %s 本页%d条 累计%d条" % (page_no, url, len(page_records), len(records)))

        next_a = soup.select_one("a.next")
        if next_a is None:
            print("找不到“下一页”按钮，结构异常，停止。")
            break
        classes = next_a.get("class") or []
        if "next-active" not in classes:       # 末页按钮被禁用
            print("“下一页”按钮已禁用，到达末页，正常停止。")
            break

        href = next_a.get("href")
        next_url = urljoin(url, href)          # ?page=2 → 完整地址
        print("  下一页 href=%s → %s" % (href, next_url))
        if not next_url.startswith("http://www.bspider.top"):
            print("下一页地址越出教学站范围，停止。")
            break
        if next_url in visited:
            print("下一页地址已访问过，停止（防止重复采集）。")
            break
        url = next_url
        time.sleep(SLEEP_SECONDS)

    # 统计按 8 个字段完全相同的重复记录（列表页同一房源会重复出现）
    unique, seen = [], set()
    for rec in records:
        key = tuple(rec)
        if key not in seen:
            seen.add(key)
            unique.append(rec)

    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    csv_path = data_dir / "houseinfo.csv"
    # 保存全部采集结果（600 条），重复条数在下方统计中单独记录
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        writer.writerows(records)

    # 回读核对
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        back = list(csv.DictReader(f))
        header = (back[0].keys() if back else f.fieldnames)

    print("-" * 50)
    print("采集页数：%d" % page_no)
    print("采集记录数（去重前）：%d" % len(records))
    print("完全相同的重复记录数：%d" % (len(records) - len(unique)))
    print("按 8 字段去重后应有：%d" % len(unique))
    print("保存到 CSV 的数据行数：%d" % len(records))
    print("回读条数：%d" % len(back))
    print("CSV 表头：%s" % (list(header) if header else None))
    print("CSV 路径：%s" % csv_path)
    print("第一条：%s" % (records[0] if records else None))


if __name__ == "__main__":
    main()
