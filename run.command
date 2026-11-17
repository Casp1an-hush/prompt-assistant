#!/bin/bash
# 双击启动 Prompt Assistant：准备环境 → 启动 → 健康检查通过后打开浏览器
cd "$(dirname "$0")" || exit 1

URL="http://localhost:8000"

# 已经在跑就直接开浏览器（探健康端点，比探首页更准）
if curl -fsS --max-time 1 "$URL/api/health" >/dev/null 2>&1; then
  open "$URL"
  exit 0
fi

if [ ! -d ".venv" ]; then
  echo "首次运行，正在准备环境（约 1 分钟）…"
  python3 -m venv .venv || { echo "创建虚拟环境失败"; read -n 1 -s -r -p "按任意键退出"; exit 1; }
  .venv/bin/pip install -q -r requirements.txt || { echo "安装依赖失败，检查网络后重试"; read -n 1 -s -r -p "按任意键退出"; exit 1; }
fi

if [ ! -f ".env" ]; then
  echo "未找到 .env，请先复制 .env.example 为 .env 并填入你的 DEEPSEEK_API_KEY。"
  read -n 1 -s -r -p "按任意键退出"
  exit 1
fi
# key 只允许当前用户读取
chmod 600 .env 2>/dev/null

echo "正在启动，浏览器会在服务就绪后自动打开…"
# 轮询健康检查，不再靠 sleep 猜启动时间
(
  for _ in $(seq 1 60); do
    if curl -fsS --max-time 1 "$URL/api/health" >/dev/null 2>&1; then
      open "$URL"
      exit 0
    fi
    sleep 0.25
  done
) &

exec .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
