# Notionに収集したテクノロジー記事をまとめる

## 実現していること

Notionは次のようなイメージ。気になったニュース記事があったら、スマホからここに格納するというのを日課にしている。

この記事を、ざっくりとまとめて、後で振り返られるようにする。

![alt text](img/image.png)

Completedがチェックされていない記事を対象に、記事の内容をまとめて、サマリをNotionに保存する。


## シークレット変数

シークレット変数は、次の方法で3種類を設定

https://docs.github.com/ja/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions

* OpenAIのAPIキーを、OPENAI_API_KEYとして保存

* NotionのAPIキーを、NOTION_API_KEYとして保存

* テーブルのURLから、https://www.notion.so/と?で挟まれている部分を、DATABASE_IDとして保存

![alt text](img/image-1.png)

## GitHub Actionsの設定

下記の記事をもとに、GitHub Actionsで定期実行を行う[yamlファイル](https://github.com/karasu1982/write_news_article/blob/main/.github/workflows/main.yaml)を作成

* [GitHub Actions入門](https://qiita.com/rapirapi/items/30fd28026408796f0ace)
* [シークレット変数を使ってGitHub Actionsで機密情報を利用する](https://qiita.com/tomo324/items/4ad0e66c94078d5b7218)
* [Github Actions を定刻に実行する方法](https://zenn.dev/no4_dev/articles/14b295b8dafbfd)

