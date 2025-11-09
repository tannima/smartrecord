#!/usr/bin/env python3
"""
智能语音思考记录器
支持语音转文字并按日期和时间戳保存
"""

import os
import sys
import datetime
import speech_recognition as sr
import threading
import time
from pathlib import Path
from pynput import keyboard

class VoiceThoughtRecorder:
    def __init__(self, storage_path="~/Desktop/Thought"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.should_stop = False
        self.should_cancel = False

        # 设置停顿检测时间（3秒）
        self.recognizer.pause_threshold = 3.0

        # 调整环境噪音
        print("正在校准麦克风...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("校准完成！")
    
    def get_today_file(self):
        """获取今天的记录文件路径"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return self.storage_path / f"{today}.txt"
    
    def save_thought(self, text):
        """保存思考内容到文件"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = self.get_today_file()
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {text}\n\n")
        
        print(f"已保存到: {file_path}")
    
    def on_press(self, key):
        """监听按键
        ESC: 取消录音（不识别）
        E键: 结束录音并识别
        """
        try:
            if key == keyboard.Key.esc:
                print("\n❌ 检测到ESC键，取消录音...")
                self.should_cancel = True
                self.should_stop = True
                return False  # 停止监听
            elif hasattr(key, 'char') and key.char in ['e', 'E']:
                print("\n⏹️  检测到E键，结束录音...")
                self.should_stop = True
                return False  # 停止监听
        except:
            pass

    def record_and_transcribe(self):
        """录音并转换为文字
        返回: (success, text)
            - success: True表示成功/取消，False表示需要重试
            - text: 识别的文字或None
        """
        print("\n🎤 请开始说话... (安静3秒自动停止 | 按E键结束 | 按ESC取消)")

        self.should_stop = False
        self.should_cancel = False
        self.audio_data = None
        self.recording_error = None

        # 在后台启动键盘监听
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        def record_audio():
            """在单独线程中录音"""
            try:
                # 每次录音创建新的麦克风实例，避免资源冲突
                with sr.Microphone() as source:
                    # 录音，等待开始说话的超时时间为30秒，最长录音120秒（2分钟）
                    # pause_threshold=3.0 表示安静3秒后停止录音
                    self.audio_data = self.recognizer.listen(source, timeout=30, phrase_time_limit=120)
            except sr.WaitTimeoutError:
                self.recording_error = "timeout"
            except Exception as e:
                self.recording_error = str(e)

        # 在后台线程开始录音
        record_thread = threading.Thread(target=record_audio, daemon=True)
        record_thread.start()

        # 等待录音完成或用户按键
        while record_thread.is_alive():
            if self.should_cancel:
                # ESC键：立即取消，等待0.5秒
                record_thread.join(timeout=0.5)
                break
            elif self.should_stop:
                # E键：需要等待pause_threshold时间让录音自然结束
                # 等待最多4秒（稍大于pause_threshold的3秒）
                print("⏳ 正在结束录音...")
                record_thread.join(timeout=4.0)
                break
            time.sleep(0.1)

        listener.stop()

        # 如果是取消（ESC键）
        if self.should_cancel:
            print("❌ 录音已取消，不进行识别")
            return (True, None)  # 取消录音，退出程序

        # 检查录音错误
        if self.recording_error == "timeout":
            if not self.should_stop:
                print("⏰ 30秒内未检测到语音输入")
            return (False, None)  # 超时，可以重试
        elif self.recording_error:
            print(f"❌ 录音错误: {self.recording_error}")
            return (False, None)  # 错误，可以重试

        # 检查是否有音频数据
        if not self.audio_data:
            # 如果是用户主动按了E键但没有录到音频，视为取消操作
            if self.should_stop:
                print("❌ 未录制到音频数据，已取消")
                return (True, None)  # 取消操作，退出程序
            else:
                print("❌ 未录制到音频数据")
                return (False, None)  # 其他错误，重试

        # 如果是手动停止（E键）或自动停止（3秒静音）
        if self.should_stop:
            print("⏹️  录音已结束")

        print("🔄 正在转换语音...")

        # 使用Google语音识别（支持中文）
        try:
            text = self.recognizer.recognize_google(self.audio_data, language='zh-CN')
            print(f"✅ 识别结果: {text}")
            self.save_thought(text)
            return (True, text)  # 成功识别
        except sr.UnknownValueError:
            print("❌ 无法识别语音内容，请重试")
            return (False, None)  # 识别失败，可以重试
        except sr.RequestError as e:
            print(f"❌ 语音服务错误: {e}")
            return (False, None)  # 服务错误，可以重试
    
    def start_recording_session(self):
        """开始录音会话"""
        print("=" * 50)
        print("🧠 智能思考记录器已启动")
        print("=" * 50)
        print("存储路径:", self.storage_path)
        print("今日文件:", self.get_today_file())
        print("\n说明:")
        print("- 程序启动后立即开始录音")
        print("- 安静超过3秒自动停止录音")
        print("- 按 E键 结束录音并识别")
        print("- 按 ESC键 取消录音（不识别）")
        print("- 最长录音时间为2分钟")
        print("- 按 Ctrl+C 退出程序")
        print("=" * 50)
        
        try:
            while True:
                success, result = self.record_and_transcribe()
                if success:
                    # 成功完成（识别成功或用户按ESC）
                    if result:
                        print("\n✨ 录音完成！程序将退出...")
                    else:
                        print("\n👋 已取消，程序将退出...")

                    # 等待1秒让用户看到消息
                    time.sleep(1)

                    # 直接退出进程，让终端自动关闭（通过exit命令）
                    sys.exit(0)
                else:
                    # 失败（识别失败、超时等），重新录音
                    print("\n🔄 准备重新录音...")
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
            sys.exit(0)

def main():
    # 检查命令行参数
    storage_path = "~/Desktop/Thought"
    if len(sys.argv) > 1:
        storage_path = sys.argv[1]

    recorder = VoiceThoughtRecorder(storage_path)
    recorder.start_recording_session()

if __name__ == "__main__":
    main()