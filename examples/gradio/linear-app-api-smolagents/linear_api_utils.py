# This code is licensed under the MIT License.
# Copyright (c) [2025] [Akihito Miyazaki]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import os
import time

#
from pprint import pprint
import requests


def request_linear(
    headers, data, url="https://api.linear.app/graphql", print_header=False
):
    response_data = None
    try:
        response = requests.post(url, headers=headers, json=data)

        response_data = response.json()
        if print_header:
            print("--- ヘッダーの表示開始 ---")
            pprint(dict(response.headers), indent=4)
            print("--- ヘッダーの表示終了 ---")

        response.raise_for_status()  # ステータスコードが200番台以外の場合に例外を発生させる
        return response_data
    except requests.exceptions.RequestException as e:
        print(response_data)
        print(f"エラーが発生しました: {e}")
        # exit(0)
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        print(f"レスポンス内容:\n{response.text}")
        # exit(0)


def load_api_key(dir="./"):
    print(f"{dir}.env")
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=f"{dir}.env")
    if "api_key" in os.environ:
        api_key = os.environ["api_key"]
        return api_key
    else:
        print("'api_key' が環境変数にありません。")
        print(".envファイルを作成し 以下の行を追加してください。")
        print("api_key=your_api_key")
        print("このファイルは.gitignoreに追加して、決して公開しないでください。")
        print(
            "Linear Settings Security&access - Personal API keysからAPI Keyは作成できます。"
        )
        exit(0)


def execute_query(label, query_text, authorization, print_header=False):
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }

    start_time_total = time.time()
    print(f"--- 処理の開始:{label} ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")

    query_dic = {"query": query_text}
    print("--- クエリの表示開始 ---")
    print(f"{query_dic['query']}")
    print("--- クエリの表示終了 ---")
    result = request_linear(headers, query_dic, print_header=print_header)
    print("--- 結果の表示開始 ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("--- 結果の表示終了 ---")
    end_time_total = time.time()
    total_time = end_time_total - start_time_total
    print(f"--- 処理の終了:{label} ---")
    print(f"合計処理時間: {total_time:.4f} 秒")

    print("")  # spacer

    return result
