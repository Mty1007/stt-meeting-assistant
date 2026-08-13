# STT Meeting Assistant

粵英混語語音識別 + 智能會議紀要生成工具

---

## 功能

- 上傳音頻（MP3 / WAV / M4A 等）
- 自動說話人分離（pyannote.audio）— 支持多人同時說話
- 雙引擎 STT 可切換：IBM Watson STT（粵語廣頻）/ ElevenLabs Scribe v1
- 逐字稿展示（帶說話人標籤 + 時間戳）
- watsonx.ai 生成結構化會議紀要（粵語 / 普通話 / 英語 三語切換）
- 顯示處理耗時 + 預估費用

---

## 項目結構

```
.
├── backend/           # Python FastAPI 後端
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   ├── routers/
│   └── services/
│       ├── audio_processor.py   # 音頻預處理（16kHz mono）
│       ├── diarization.py       # 說話人分離（pyannote）
│       ├── ibm_stt.py           # IBM Watson STT
│       ├── elevenlabs_stt.py    # ElevenLabs Scribe v1
│       └── watsonx.py           # watsonx.ai 紀要生成
└── frontend/          # Next.js 14 前端
    └── src/
        ├── app/
        ├── components/
        └── lib/api.ts
```

---

## 快速開始

### 1. 安裝系統依賴

```bash
# macOS
brew install ffmpeg

# 後端 Python 依賴
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置環境變量

```bash
cp backend/.env.example backend/.env
# 編輯 backend/.env，填入所有 API Key
```

需要的 Key：
| 變量 | 獲取地址 |
|------|---------|
| `IBM_STT_API_KEY` | IBM Cloud → Speech to Text 服務 |
| `IBM_STT_URL` | 同上，服務頁面的 URL |
| `ELEVENLABS_API_KEY` | elevenlabs.io → Profile → API Key |
| `WATSONX_API_KEY` | IBM Cloud → watsonx.ai |
| `WATSONX_PROJECT_ID` | watsonx.ai → Projects → Project ID |
| `HUGGINGFACE_TOKEN` | huggingface.co → Settings → Access Tokens（需接受 pyannote 模型授權）|

### 3. 接受 pyannote 模型授權

pyannote.audio 需要先在 Hugging Face 接受使用條款：
1. 登錄 [huggingface.co](https://huggingface.co)
2. 進入 [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. 點擊 "Agree and access repository"
4. 同理接受 [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

### 4. 啟動後端

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API 文檔：http://127.0.0.1:8000/docs

### 5. 啟動前端

```bash
# 需要 Node.js >= 18
cd frontend
npm install
npm run dev
```

打開：http://localhost:3000

---

## API 接口

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/api/upload` | 上傳音頻，返回 `job_id` |
| POST | `/api/transcribe` | 運行 STT，返回逐字稿 |
| POST | `/api/summarize` | 生成會議紀要（選擇語言）|
| GET  | `/health` | 健康檢查 |

---

## 技術棧

| 層 | 技術 |
|----|------|
| 前端 | Next.js 15, React 19, TailwindCSS |
| 後端 | Python FastAPI, uvicorn |
| 說話人分離 | pyannote.audio 3.x |
| STT | IBM Watson STT + ElevenLabs Scribe v1 |
| AI 分析 | IBM watsonx.ai (Granite-13b-chat-v2) |
| 監控 | Instana APM |
