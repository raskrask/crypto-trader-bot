# crypto-trader-bot


# Crypto Trading Bot - Prompt

## 目的
暗号通貨の自動取得・分析・取引を行うボットを開発し、AI を活用したトレード戦略を構築する。
- **使用する取引所**: CoinCheck(BTC/JPY) , Binance
- **AIエンジン**: 未定
- **取引ロジック**: テクニカル指標 + AI分析

## 技術スタック
- **開発言語**_: Python
- **フロントエンド**: Streamlit
- **バックエンド**: FastAPI、Uvicorn
- **インフラ環境**: AWS Lambda / S3, Docker(frontend/backend)
- **開発環境**: Mac, VSCode, Docker


---
## 構成

### 1. 基本インターフェース作成
- データ取得・取引実行の基本機能を実装
  - 為替レート取得（Yahoo Finance）
    売買取引市場はCoinCheckを対象とするため、対象通貨はJPY限定となるためUSDTとの計算が必要。
  - [CoinCheck API ドキュメント](https://coincheck.com/ja/documents/exchange/api)

### モデルパイプライン
+ CryptoTrainingDataset
  - Binance API からohlcvデータ取得し機械学習用のデータセットを作成
+ FeatureDatasetModel
  - テクニカル指標としてSMA, ボリンジャーバンド, RSI 関連を説明変数として追加
  - 過去のデータをラグ10〜15日をまとめて説明変数として追加
  - MinMaxScalerでデータスケーリング
  - 未来日の終値を目的変数
+ EnsembleModel
  - 学習済みモデルを保存
  - 自動チューニング（ハイパーパラメータ最適化)
  - 回帰分析モデルなどいくつかのモデルをアンサンブルして予測を実行し、次の取引の判断に利用
+ Evaluation
  - モデルの検証
  - 過去データを使って予測の精度を評価
  - MSE（平均二乗誤差）や RMSE（ルート平均二乗誤差）で誤差を計測
  - 学習データとテストデータを分割し、オーバーフィッティングを防ぐ
  - 検証結果を記録して、今後の改善に役立てる

### 2. Bot（Python + AWS）の基本構成作成
- Python によるデータ処理と AWS を活用した実行環境構築
- AWS Lambda を利用した定期実行
- AWS SAM によるインフラ管理
- Docker での開発環境構築
- 定期学習

### 3. Slack 通知の Webhook 設定
- 取引結果やアラートを Slack に通知
- エラーハンドリングも含めた実装

### 4. AWS Lambda 作成
- CoinCheck API からのデータ取得
- S3 への保存と履歴管理
- 定期実行設定（CloudWatch Events）

### 5. AI 分析（AWS Bedrock）
- **価格予測**（短期・中期）
- **システムトレード**（機械的な売買ルール）
- **未来の特徴量の回帰分析予測**
- **トレンド判定**（上昇 or 下降）
- **ボラティリティの検出**（急騰 or 急落の予測）
- **ニュースやセンチメント分析を加えた戦略**
  - VIX が 30 以上 & S&P500 が下落トレンド → BTC のショート戦略
  - BTC の取引所流入量が急増 & オープンインタレストが高い → 高ボラティリティに備えてポジション縮小
  - ステーブルコイン供給量増加 & BTC ドミナンス低下 → アルトコインの買い戦略
  - 先物市場を元に購入戦略を立てる
  - 米国カレンダーなどの時事情報と組み合わせる

### 6. 購入データの保存と分析
- **取引結果の記録**（勝率・利益率の計算）
- **多軸での分析**（VIT, GOLD など）
- **過去データの収集・バックテスト**（CoinCheck の過去データを S3 や DynamoDB に保存し、分析）

### 7. セキュリティと API 管理
- **API エラー時のリトライ戦略**（レートリミット超過、ネットワークエラー対応）
- **価格変動が激しい時の対応**
- **Bot の取引量を調整し、市場への影響を最小化**

### 8. 対象通貨の選択
- CoinCheck で **流動性の高い通貨ペア** を選択
- BTC/USDT, ETH/USDT, アルトコイン？

### 9. アルゴリズム選定
- **トレード戦略の検討**
  - **スキャルピング**（短期売買）
  - **デイトレード**（1日内完結）
  - **スイングトレード**（数日～数週間）
  - **レバレッジと指値の設定**

### 10. リスク管理とロスカットの設定
- 取引ごとの **最大損失額**（例: 5% 以下）
- **トレーリングストップ** の活用

### 11. 機械学習の活用と数値予測
- **ランダムフォレスト, LSTM（長短期記憶ネットワーク）, XGBoost などの活用**
- **AI の予測とテクニカル指標（移動平均線、RSI、ボリンジャーバンド）を組み合わせる**

## 実装スケジュール
- **フェーズ 1:** CoinCheck API の基本機能 & データ保存の実装
- **フェーズ 2:** AWS Lambda の設定 & Slack 通知の実装
- **フェーズ 3:** AI 予測の導入 & システムトレードの実装
- **フェーズ 4:** リスク管理 & バックテスト環境の構築

## 目標
- **収益性の高い自動売買 Bot の構築**
- **AI を活用した精度の高いトレード戦略の実装**
- **安全かつ拡張可能なインフラの構築**


# セットアップ

### Python初期設定
```
python3.11 -m venv venv311
source venv311/bin/activate
pip install --upgrade pip
pip install -U -r frontend/requirements.txt
pip install -U -r backend/requirements.txt
```

### sam初期設定
- S3 Bucket作成
```
sam deploy
sam deploy --guided
```

### Docker
```
docker-compose build && docker-compose up -d
docker exec -it crypto-trader-bot-backend-1 bash
docker-compose logs -f backend
```

### 作業メモ
```
pip3 freeze > requirements.txt
aws s3 ls s3://crypto-trader-bot/crypto_data/
```

