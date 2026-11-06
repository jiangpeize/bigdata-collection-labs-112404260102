# -*- coding: utf-8 -*-
"""第三阶段：读取第二阶段的 data/houseinfo.csv，用 pymysql 批量入库 smartpark_lab.houseinfo。"""
import csv
import os

import pymysql

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "houseinfo.csv")

# CSV 表头即表的 8 个业务字段（id 是自增主键，不入参）
FIELDS = ["title", "house", "address", "struct", "area", "floor", "maketime", "price"]

DB = dict(
    host=os.environ.get("MYSQL_HOST", "mysql"),  # compose 网络里的 mysql 服务名
    port=3306,
    user="student",
    password="123456",
    database="smartpark_lab",
    charset="utf8mb4",
)


def main():
    # 1. 读取 CSV，按 8 个字段整理入库参数（每行转成一个 8 元组）
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [[(rec.get(k) or "").strip() for k in FIELDS] for rec in reader]
    print("CSV 数据行数:", len(rows))

    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM houseinfo")
        before = cur.fetchone()[0]
        print("入库前条数:", before)

        if before > 0:
            # 避免重复插入：重跑时表中已有同批数据，直接跳过，不再 INSERT
            print("表中已有数据（%d 条），跳过插入，避免同批数据重复入库" % before)
        else:
            sql = (
                "INSERT INTO houseinfo "
                "(title, house, address, struct, area, floor, maketime, price) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            try:
                cur.executemany(sql, rows)  # 批量插入，参数化防注入
                conn.commit()               # 成功：提交事务
                print("本次新增:", cur.rowcount)
            except Exception:
                conn.rollback()             # 失败：整体回滚，不留半批数据
                raise
        cur.execute("SELECT COUNT(*) FROM houseinfo")
        after = cur.fetchone()[0]
        print("入库后条数:", after)
    finally:
        cur.close()    # 关闭游标
        conn.close()   # 关闭连接


if __name__ == "__main__":
    main()
