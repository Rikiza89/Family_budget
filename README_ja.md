# README_ja.md

# 家族予算管理アプリ

複数の家族メンバーで家族の予算を管理し、支出を追跡し、将来のイベントを計画するための包括的なDjangoウェブアプリケーションです。デスクトップからモバイルデバイスまで、完全にレスポンシブに対応しています。

## 主な機能

- **ダッシュボード**: 収入、支出、貯蓄、残高をリアルタイムで一目で確認
- **取引ログ**: 収入、支出、貯蓄を説明付きで記録
- **予算管理**: カテゴリごとに支出制限を設定・監視
- **定期取引**: 定期的な支出と収入を自動化
- **将来のイベント**: 将来の経済的イベントを計画・追跡
- **家族管理**: 複数の家族メンバーが共有データにアクセス可能
- **カテゴリ管理**: カスタムの収入、支出、貯蓄カテゴリを作成
- **レスポンシブデザイン**: デスクトップ、タブレット、モバイルにシームレスに対応
- **多言語対応**: 英語と日本語のインターフェース

## 技術スタック

- **バックエンド**: Django 4.2.7
- **フロントエンド**: Bootstrap 5.3、HTML5、CSS3、JavaScript
- **データベース**: SQLite（デフォルト、PostgreSQL/MySQLに変更可能）
- **認証**: Django組み込み認証システム

## インストール

### 前提条件

- Python 3.8以上
- pip（Pythonパッケージインストーラー）
- 仮想環境（推奨）

### セットアップ手順

1. **リポジトリをクローン**
```bash
git clone https://github.com/Rikiza89/family-budget-app.git
cd family-budget-app
```

2. **仮想環境を作成・有効化**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **依存関係をインストール**
```bash
pip install -r requirements.txt
```

4. **マイグレーションを実行**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **スーパーユーザー（管理者アカウント）を作成**
```bash
python manage.py createsuperuser
```

6. **開発サーバーを起動**
```bash
python manage.py runserver
```

7. **アプリケーションにアクセス**
ブラウザで `http://127.0.0.1:8000/` に移動してください

## 使用方法

### 家族の作成

1. スーパーユーザーアカウントでログイン
2. Django管理画面 (`http://127.0.0.1:8000/admin/`) に移動
3. 新しい家族を作成
4. ユーザーを家族にリンクするメンバーを作成
5. `http://127.0.0.1:8000/app/` のダッシュボードにアクセス

### ダッシュボード

財務状況を一目で確認：
- 当月の収入、支出、貯蓄
- 予算状況とアラート
- 次の30日以内の予定イベント
- カテゴリ別の内訳

### 取引の記録

1. **ログ** セクションに移動
2. 取引詳細を入力（カテゴリ、金額、日付、説明）
3. 「ログを追加」をクリック
4. 日付範囲フィルターで特定の取引を表示

### 予算の管理

1. **予算** セクションに移動
2. 特定のカテゴリに支出制限を設定
3. 支出を制限に対して監視
4. 制限に近づいたまたは超過した場合にアラートを表示

### 定期取引

1. **定期** セクションに移動
2. 定期取引を作成（毎日、毎週、毎月など）
3. 開始日と終了日を設定
4. 必要に応じて有効/無効を切り替え

### 将来のイベント

1. **イベント** セクションに移動
2. 将来の経済的イベント（収入または支出）を追加
3. 大きな支出や収入に備える

### 家族設定

1. **設定** にアクセスして以下を管理：
   - 家族情報と認可コード
   - 家族メンバー
   - カスタムカテゴリ

## プロジェクト構成

```
family-budget-app/
├── manage.py
├── requirements.txt
├── README_ja.md
├── LICENSE_ja.md
├── family_budget_app/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── family_app/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── templates/
│   │   ├── base_ja.html
│   │   ├── dashboard_ja.html
│   │   ├── logs_ja.html
│   │   ├── budget_ja.html
│   │   ├── recurring_ja.html
│   │   ├── events_ja.html
│   │   └── family_settings_ja.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
└── db.sqlite3
```

## 構成

### 環境変数

ルートディレクトリに `.env` ファイルを作成してください：

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### データベース設定

デフォルト: SQLite

PostgreSQL を使用する場合は、`settings.py` を更新してください：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'family_budget',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## APIの概要

### モデル

- **Family**: 個別の家族ユニットを表現
- **Member**: ユーザーを家族にリンク
- **Category**: カスタム取引カテゴリ
- **Log**: 個別取引
- **RecurringLog**: 自動定期取引
- **BudgetLimit**: カテゴリごとの支出制限
- **FutureEvent**: 計画された将来の取引

### ビュー

- `dashboard`: メインダッシュボード
- `logs_view`: 取引管理
- `budget_view`: 予算管理
- `recurring_view`: 定期取引
- `events_view`: 将来のイベント
- `family_settings`: 家族設定

## モバイル最適化

アプリケーションは以下を含む完全にレスポンシブです：
- モバイルファーストなデザインアプローチ
- タッチフレンドリーなボタンと入力
- 小さい画面向けに最適化されたナビゲーション
- レスポンシブテーブルとチャート
- 高速な読み込み時間

## 言語サポート

アプリは英語と日本語の両方のインターフェースをサポートしています。両言語用のテンプレートが用意されています：
- 英語テンプレート: `template.html`
- 日本語テンプレート: `template_ja.html`

## デプロイメント

### 本番環境チェックリスト

1. `settings.py` で `DEBUG=False` に設定
2. `ALLOWED_HOSTS` を更新
3. 本番用データベースを使用（PostgreSQL推奨）
4. 強力な `SECRET_KEY` を設定
5. HTTPSを使用
6. 適切なログを設定
7. 本番用サーバーを使用（Gunicorn、uWSGI）

### Gunicornでのデプロイメント

```bash
pip install gunicorn
gunicorn family_budget_app.wsgi:application --bind 0.0.0.0:8000
```

### Dockerでのデプロイメント

`Dockerfile` を作成してください：
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "family_budget_app.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## トラブルシューティング

### 静的ファイルが読み込まれない場合

```bash
python manage.py collectstatic
```

### データベースエラー

```bash
python manage.py makemigrations
python manage.py migrate
```

### ポートが既に使用されている場合

```bash
python manage.py runserver 8001
```

## 貢献

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを開く

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は [LICENSE_ja](LICENSE_ja.md) ファイルを参照してください。

## サポート

問題、質問、提案がある場合：
- GitHubイシューを開く
- 既存のドキュメントを確認
- トラブルシューティングセクションをご覧ください

## 謝辞

- Djangoフレームワーク
- Bootstrap CSSフレームワーク
- Bootstrap Icons
- 貢献者とユーザー

---

**バージョン**: 1.0.0  
**最終更新**: 2025年10月10日
**Pythonバージョン**: 3.8以上


---
