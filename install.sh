#!/bin/bash

echo "🔧 开始安装语音思考记录器依赖..."

# 检查是否安装了 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未找到 Homebrew，请先安装 Homebrew"
    echo "安装命令: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# 安装 Python 依赖
echo "📦 安装 Python 包..."
pip3 install SpeechRecognition pyaudio pynput

# 检查是否需要安装 portaudio (pyaudio 的依赖)
if ! brew list | grep -q "portaudio"; then
    echo "📦 安装 portaudio..."
    brew install portaudio
fi

echo "✅ 依赖安装完成！"
echo ""
echo "📝 使用说明:"
echo "1. 保存 Python 脚本为 voice_recorder.py"
echo "2. 运行: python3 voice_recorder.py"
echo "3. 或者设置键盘快捷键来运行该脚本"
echo ""
echo "🎯 下一步: 设置键盘快捷键"