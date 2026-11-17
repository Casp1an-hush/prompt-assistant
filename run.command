#!/bin/bash
# Prompt Assistant 启动器：准备环境 → 修复坏服务 → 稳健启动 → 就绪后才开浏览器
# 双击本文件即可。全部启动逻辑集中在这一个文件里；桌面快捷方式只转发到这里，
# 因此以后只需维护这一处，不会出现「两份脚本各改一半」的分叉。
cd "$(dirname "$0")" || { echo "无法进入项目目录"; read -n 1 -s -r -p "按任意键退出"; exit 1; }

URL="http://localhost:8000"

# 健康判据：必须读到完整的 </html>。
# 关键：不能只看响应头，也不能只探 /api/health —— 半死的服务会回 200 头、
# 甚至 health 端点能回，但首页正文发不出来（浏览器白屏 ERR_CONTENT_LENGTH_MISMATCH）。
# 只有完整首页才能证明「服务活着 + 页面能发出身体」。
page_ok() { curl -fsS --max-time 2 "$URL/" 2>/dev/null | grep -q '</html>'; }

# 已经在跑且页面完整 → 直接开浏览器
if page_ok; then
  open "$URL"
  exit 0
fi

# 端口被占但页面不完整 → 是坏的旧进程，杀掉再重启
# 用 lsof 判断端口占用，比 curl 更可靠（能抓到「有头无身」的半死状态）
if lsof -nP -iTCP:8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "检测到旧服务无响应（端口被占但页面不完整），正在重启…"
  OLD_PIDS=$(lsof -nP -iTCP:8000 -sTCP:LISTEN -t 2>/dev/null)
  [ -n "$OLD_PIDS" ] && kill $OLD_PIDS 2>/dev/null
  sleep 1
fi

# 首次运行：自动准备环境
if [ ! -d ".venv" ]; then
  echo "首次运行，正在准备环境（约 1 分钟）…"
  python3 -m venv .venv || { echo "创建虚拟环境失败"; read -n 1 -s -r -p "按任意键退出"; exit 1; }
  .venv/bin/pip install -q -r requirements.txt || { echo "安装依赖失败，检查网络后重试"; read -n 1 -s -r -p "按任意键退出"; exit 1; }
fi

# 还没配 key：交互式询问并校验，避免用户手动复制 .env
if [ ! -f ".env" ]; then
  echo ""
  echo "════════════════════════════════════════"
  echo "  第一次使用，需要填一次 DeepSeek 的 key"
  echo "════════════════════════════════════════"
  echo ""
  echo "key 是一串以 sk- 开头的英文字母和数字，"
  echo "没有中文、没有空格，长度大约 30 多个字符。"
  echo "获取方法：浏览器打开 https://platform.deepseek.com"
  echo "  → 登录 → 左侧「API keys」→ 点创建 → 复制那串 sk-xxx"
  echo ""
  while true; do
    read -r -p "把 key 粘贴到这里，然后按回车：" KEY
    # 只保留英文字母、数字和连字符，自动过滤中文/空格/全角符号
    KEY=$(printf '%s' "$KEY" | LC_ALL=C tr -cd '[:alnum:]-')
    if [ -z "$KEY" ]; then
      echo "⚠️  没有检测到任何有效字符。请重新复制那串 sk- 开头的 key 再粘。"
      continue
    fi
    case "$KEY" in
      sk-*) ;;
      *) echo "⚠️  这串不是以 sk- 开头，不像 DeepSeek 的 key。请确认复制的是「API keys」页面里那一串。"; continue ;;
    esac
    if [ ${#KEY} -lt 20 ]; then
      echo "⚠️  key 太短（只有 ${#KEY} 个字符），可能没复制完整。请重新复制完整的一串。"
      continue
    fi
    break
  done
  printf 'DEEPSEEK_API_KEY=%s\n' "$KEY" > .env
  echo ""
  echo "✓ 已保存 key（长度 ${#KEY}），开始启动…"
  echo ""
fi
# key 只允许当前用户读取
chmod 600 .env 2>/dev/null

echo "正在启动，浏览器会在服务就绪后自动打开…"
echo "用完直接关掉这个窗口即可停止。"
# 轮询健康判据，就绪才开浏览器（不靠 sleep 猜）；最多等约 30 秒
(
  for _ in $(seq 1 120); do
    if page_ok; then
      open "$URL"
      exit 0
    fi
    sleep 0.25
  done
) &

exec .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
