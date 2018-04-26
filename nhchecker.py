#!/usr/bin/env python3
import argparse
import json
import os
import requests
import time
from typing import Iterable

API_URL = "https://api.nicehash.com/api"
USER_JSON_FILENAME = "user.json"
USER_JSON_PATH = os.path.join(os.path.dirname(__file__), USER_JSON_FILENAME)
IS_MILLI = False
IS_READABLE = False


def create_json_file() -> None:
    """ user.jsonの雛形を作り保存する """
    data = {"addr": "", "id": "", "key": ""}
    with open(USER_JSON_PATH, mode="w") as fp:
        json.dump(data, fp)


def get_userdata(keys: Iterable[str]) -> dict:
    """ ユーザ情報を必要なキーがあるかどうか確認してから返す """
    if not os.path.exists(USER_JSON_PATH):
        raise Exception("{}が無いよ".format(USER_JSON_FILENAME))
    data = json.load(open(USER_JSON_PATH))
    for key in keys:
        if key not in data or data[key] == "":
            raise Exception("{}に必要なキー：{}が存在しないか値が空だよ"
                            .format(USER_JSON_FILENAME, key))
    return data


def download_json(params: dict) -> dict:
    """ APIにアクセスしjson["result"]を返す """
    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()
    return resp.json()["result"]


def print_result(value: float, prefix: str = "", suffix: str = "") -> None:
    """ オプションに合わせた書式で表示 """
    if IS_MILLI:
        unit = "mBTC"
        value = "{:.3f}".format(value * 1000)
    else:
        unit = "BTC"
        value = "{:.5f}".format(value)
    print("{}{} {}{}".format(prefix, value, unit, suffix)
          if IS_READABLE else value)


def show_stats() -> None:
    """
    stats.provider.exから過去(デフォルト1時間)の収益データを得て
    1日あたりの収益量を計算し表示
    """
    PERIOD = 1  # hour

    userdata = get_userdata(("addr",))

    params = {
        "method": "stats.provider.ex",
        "addr": userdata["addr"],
        "from": int(time.time())-(3600*PERIOD+300)
    }
    data = download_json(params)

    unpaid = 0
    for algo in data["current"]:
        unpaid += float(algo["data"][1])

    profitability = 0
    for algo in data["past"]:
        for older, newer in zip(algo["data"], algo["data"][1:]):
            old_balance, new_balance = float(older[2]), float(newer[2])
            # 支払いのタイミングを挟むとbalanceが0に戻るための処理
            profitability += (new_balance - old_balance
                              if new_balance >= old_balance else new_balance)
    profitability = profitability*(24/PERIOD)

    print_result(unpaid)
    print_result(profitability, suffix="/day")


def show_balance() -> None:
    """ NiceHash walletのbalanceを表示 """
    userdata = get_userdata(("id", "key"))
    params = {
        "method": "balance", "id": userdata["id"], "key": userdata["key"]
    }
    balance = float(download_json(params)["balance_confirmed"])

    print_result(balance)


def main() -> None:
    class MyArgParser(argparse.ArgumentParser):
        def __init__(self):
            super().__init__()

        def error(self, message):
            if not os.path.exists(USER_JSON_PATH):
                create_json_file()
                print("空の{}を作成したから中身を埋めてね"
                      .format(USER_JSON_FILENAME))
            self.print_help()
            exit(2)

    parser = MyArgParser()
    parser.add_argument("command", choices=["stats", "balance"])
    parser.add_argument("-m", "--milli",
                        help="単位をmBTCにする", action="store_true")
    parser.add_argument("-r", "--human_readable",
                        help="単位を付けて表示", action="store_true")
    args = parser.parse_args()

    global IS_MILLI, IS_READABLE
    IS_MILLI, IS_READABLE = args.milli, args.human_readable
    if args.command == "stats":
        show_stats()
    elif args.command == "balance":
        show_balance()


if __name__ == "__main__":
    main()
