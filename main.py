# -*- coding: utf-8 -*-
# secretsに登録した環境変数の呼び出し
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
model="gpt-4o-mini"

# 記事作成

# Notionに格納した情報をもとに、記事化

import requests
import pandas as pd

headers =  {
    'Notion-Version': '2022-06-28',
    'Authorization': 'Bearer ' + NOTION_API_KEY,
    'Content-Type': 'application/json',
}

# CompletedがFalse（デフォルト）の記事を取得
json_data = {
    "filter": {
        "property": "Completed",
        "checkbox": {
            "equals": False
        }
    }
}

# データ取得
url = 'https://api.notion.com/v1/databases/' + DATABASE_ID + '/query'

db_response = requests.post(url, headers=headers, json = json_data)
db_result = db_response.json().get("results")

# 変数分のlist
names = []
urls = []
page_ids = []

for d in db_result:
  names.append(d['properties']['Name']['title'][0]['plain_text'])
  urls.append(d['properties']['URL']['url'])
  page_ids.append(d["id"])

df = pd.DataFrame({'name': names, 'url':urls, 'page_id':page_ids})

# 記事が取得されない場合は、以降の処理は行わない
if len(df) >= 1:

  # 各ページの情報を取得
  contents = []

  for i, d in df.iterrows():

    PAGE_ID = d['page_id']
    block_url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"

    block_response = requests.get(block_url, headers=headers)
    block_result = block_response.json()

    _b = []

    # 力技で各ページの内容を取得
    for block in block_result.get("results"):
      try:
        _b.append(block[block.get("type")]["rich_text"][0]["plain_text"])
      except:
        continue

    contents.append("\n".join(_b))

  df["contents"] = contents

  # 取得した記事のCompletedをTrueへ

  for i, d in df.iterrows():
    PAGE_ID = d['page_id']
    url = 'https://api.notion.com/v1/pages/' + PAGE_ID

    json_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Completed" : {
                "checkbox": True
            }
        }
    }

    response = requests.patch(url, headers=headers, json = json_data)

  # 生成AIで記事をまとめる
  from langchain.chat_models import ChatOpenAI
  from langchain.prompts import PromptTemplate

  llm = ChatOpenAI(temperature=0, model=model, openai_api_key=OPENAI_API_KEY)

  prompt_template = PromptTemplate.from_template(
    template = """
    あなたはAIのテクノロジー記事を書くブロガーです。
    次の内容を日本語で要約して、記事を書いてください。500文字以内で、日本語で出力してください。
    ###
    {article}
    """)

  chain = prompt_template | llm

  outputs = []

  for i, d in df.iterrows():
    article = d['name'] + "\n" + d['contents']

    res = chain.invoke({"article": article})
    result = res.content

    outputs.append(result)

  # 作成された記事をフォーマット

  from datetime import date

  today = date.today()
  today_str1 = today.strftime('%Y-%m-%d')
  today_str2 = today.strftime('%Y%m%d')

  content = f"# {today_str1}のAI・データサイエンスニュース\n\n"

  for d1, d2, out in zip(df["name"], df["url"], outputs):
    content += f"## {d1}\n\n"
    content += f"{d2}\n\n"
    content += f"{out}\n\n"
    content += f"---\n\n"

  print(content)

  # ファイルに書き込む
  file_path = f"blob/news_{today_str2}.md"
  with open(file_path, "w", encoding="utf-8") as file:
      file.write(content)