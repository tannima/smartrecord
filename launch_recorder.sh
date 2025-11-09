#!/bin/bash

# 语音思考记录器启动脚本
# 使用方法: ./launch_recorder.sh

# 脚本路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VOICE_RECORDER="$SCRIPT_DIR/voice_recorder.py"
VENV_PATH="$SCRIPT_DIR/.venv"

# 检查脚本是否存在
if [ ! -f "$VOICE_RECORDER" ]; then
    echo "❌ 未找到 voice_recorder.py 脚本"
    echo "请确保脚本在同一目录下"
    exit 1
fi

# 创建新的终端窗口来运行语音记录器
# 如果有虚拟环境则激活，程序结束后自动关闭终端
if [ -d "$VENV_PATH" ]; then
    osascript -e "
    tell application \"Terminal\"
        activate
        do script \"cd '$SCRIPT_DIR' && source .venv/bin/activate && python3 '$VOICE_RECORDER' && exit\"
    end tell
    "
else
    osascript -e "
    tell application \"Terminal\"
        activate
        do script \"cd '$SCRIPT_DIR' && python3 '$VOICE_RECORDER' && exit\"
    end tell
    "
fi

echo "🎤 语音记录器已在新终端窗口中启动"