# kita127.github.io
my web site

## URL

https://kita127.github.io/

## 使用テンプレート

https://startbootstrap.com/themes/resume/

## Markdown記事のHTML生成

test_design 配下の Markdown 記事を HTML に変換するには、次の手順で実行します。

1. 依存ライブラリをインストールします。

```bash
python3 -m pip install markdown pygments
```

2. リポジトリのルートで、生成スクリプトを実行します。

```bash
python3 scripts/render_test_design_posts.py
```

このコマンドは、test_design 配下の .md ファイルを検索し、各ファイルと同じディレクトリに .html を生成します。
生成された HTML では、Markdown の見出し・段落・コードブロックなどが記事レイアウト用のスタイルで表示されます。

### 使用しているライブラリ

- markdown: Markdown の構文を HTML に変換するために使用しています。
- pygments: コードブロックのシンタックスハイライトを行うために使用しています。
- css/article-posts.css: 記事ページの見た目を整えるためのスタイルシートです。
