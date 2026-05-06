# YOLO Model Registry

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-orange.svg)

`YOLO Model Registry` 是一個自動化的靜態資源管理系統，旨在解決行動裝置應用程式（App）動態取得最新 YOLO 模型權重與下載連結的需求。透過此專案，您的 App 可以擺脫硬編碼（Hardcode）網址的限制，實現模型版本的無縫更新。

## 🌟 核心功能

* **自動化更新**：透過 GitHub Actions 定期檢查 Ultralytics 官方發布的最新 Release。
* **靜態對照表生成**：自動產出標準化 JSON 格式的模型清單（Model Registry）。
* **版本追蹤**：記錄每個模型的版本編號、任務類型、檔案大小與下載網址。
* **高可用性**：支援將模型鏡像（Mirror）同步至雲端儲存空間（如 S3/GCP/Cloudflare R2）。

## 🏗 技術架構

1.  **資料抓取**：使用 Python 腳本串接 GitHub API 取得 `ultralytics/assets` 的最新 Release 資訊。
2.  **處理邏輯**：過濾並格式化模型資訊，生成包含特定版本號的直接下載網址。
3.  **自動佈署**：由 GitHub Actions 觸發，將生成的 `yolo_models.json` 推送至專案分支，透過 GitHub Pages 或是您的 CDN 提供服務。

## 🚀 快速開始

### 1. 取得模型清單
您的 App 只需要發起一個 GET 請求至以下 URL，即可取得最新的模型對照表：
`https://<your-username>.github.io/yolo-model-registry/yolo_models.json`

### 2. JSON 格式範例
```json
{
  "version": "v8.3.0",
  "last_updated": "2026-05-06T11:00:00Z",
  "models": [
    {
      "name": "yolo11n",
      "version": "YOLO11",
      "task": "Object Detection",
      "download_url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
      "file_size_mb": 5.3
    }
  ]
}
```

## 🛠 自動化流程設定

### 本地開發
1. 安裝依賴環境：
   ```bash
   pip install requests
   ```
2. 執行產出腳本：
   ```bash
   python src/generate_models.py
   ```

### GitHub Actions 設定
本專案已配置 `.github/workflows/update-models.yml`，預設於每日 UTC 00:00（台灣時間 08:00）執行自動更新檢查。

## 📂 專案目錄結構
```text
├── .github/workflows/
│   └── update-models.yml    # CI/CD 自動化腳本
├── src/
│   └── generate_models.py       # 模型清單產出程式碼
├── yolo_models.json             # App 直接存取的對照表檔案
└── README.md                    # 本文件
```

## 📝 授權條款
本專案採用 [MIT License](LICENSE) 授權。模型權重檔案之版權歸原作者（Ultralytics）所有。