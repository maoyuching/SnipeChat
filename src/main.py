import sys
import os
import io
import json
import base64
import keyboard
import pyautogui
from PIL import Image, ImageGrab
from PySide6.QtWidgets import (QApplication, QSystemTrayIcon, 
                              QMenu, QMessageBox, QWidget)
from PySide6.QtGui import QIcon, QAction, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
import pyperclip  # 新增导入
import pystray
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import openai
import requests
from pynput import keyboard as pynput_keyboard

class Worker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, image_data, parent=None):
        super().__init__(parent)
        self.image_data = image_data

    def run(self):
        try:
            # 使用硅基流动的API，但配置成OpenAI格式
            client = openai.OpenAI(
                api_key="sk-ajfsxvsfseqdkknlyiilbbfugrmocinwyzuxaskqazwxqbhj",  # 替换为你的API密钥
                base_url="https://api.siliconflow.cn/v1"
            )

            # 准备消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url" :f"data:image/png;base64,{self.image_data}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "text",
                            "text": "截图显示用户正在输入，请你分析截图内容后，直接以用户的口吻给出回复，不要有多余的文字。要求回复简洁，不要有回车换行"
                        },
                    ],
                }
            ]
            
            # 调用API - 使用Qwen-VL模型
            response = client.chat.completions.create(
                model="Qwen/Qwen2-VL-72B-Instruct",  # 硅基流动上的千问视觉模型
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            reply = response.choices[0].message.content
            self.finished.emit(reply)
        except Exception as e:
            self.error.emit(str(e))

class ScreenshotTool(QWidget):
    def __init__(self):
        super().__init__()
        
        # 初始化系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # 准备一个图标文件
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 添加快捷键设置选项
        shortcut_action = QAction("设置快捷键", self)
        shortcut_action.triggered.connect(self.show_shortcut_settings)
        tray_menu.addAction(shortcut_action)
        
        # 添加退出选项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 设置全局快捷键 (默认Ctrl+Alt+Q)
        self.shortcut = "ctrl+alt+q"
        self.setup_global_hotkey()

        # 显示通知
        self.tray_icon.showMessage(
            "截图聊天神器", 
            "程序已启动，使用Ctrl+Alt+Q截图", 
            QSystemTrayIcon.Information, 
            3000
        )


    def setup_global_hotkey(self):
        """设置全局快捷键"""
        # 使用pynput监听全局快捷键
        def on_activate():
            print("user capture and analyze ")
            self.capture_and_analyze()
        
        self.hotkey = pynput_keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+q': on_activate,
        })
        self.hotkey.start()

    def capture_and_analyze(self):
        """捕获屏幕并发送给AI分析"""
        try:
            # 使用pyautogui截图
            screenshot = pyautogui.screenshot()
            
            # 转换为base64
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # 创建工作线程处理AI请求
            self.worker = Worker(img_str)
            self.worker.finished.connect(self.handle_ai_response)
            self.worker.error.connect(self.handle_ai_error)
            self.worker.start()
            
            self.tray_icon.showMessage(
                "截图聊天神器", 
                "正在分析截图...", 
                QSystemTrayIcon.Information, 
                2000
            )
        except Exception as e:
            self.tray_icon.showMessage(
                "错误", 
                f"截图失败: {str(e)}", 
                QSystemTrayIcon.Critical, 
                3000
            )

    @Slot(str)
    def handle_ai_response(self, reply):
        """处理AI回复并插入到光标位置"""
        print("ai response is ==>" + reply)
        try:


            # 使用pyperclip复制回复内容
            pyperclip.copy(reply)
            # 使用快捷键粘贴
            pyautogui.hotkey('ctrl', 'v')

            print("pyautogui has write reply")
            
            self.tray_icon.showMessage(
                "截图聊天神器", 
                "回复已插入", 
                QSystemTrayIcon.Information, 
                2000
            )
        except Exception as e:
            self.tray_icon.showMessage(
                "错误", 
                f"插入回复失败: {str(e)}", 
                QSystemTrayIcon.Critical, 
                3000
            )

    @Slot(str)
    def handle_ai_error(self, error_msg):
        """处理AI错误"""
        print("ai error is " + error_msg)
        self.tray_icon.showMessage(
            "AI分析错误", 
            error_msg, 
            QSystemTrayIcon.Critical, 
            3000
        )

    def show_shortcut_settings(self):
        """显示快捷键设置对话框"""
        msg = QMessageBox()
        msg.setWindowTitle("设置快捷键")
        msg.setText(f"当前快捷键: {self.shortcut}\n\n请输入新的快捷键组合:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        # 这里可以添加更复杂的快捷键设置UI
        result = msg.exec_()
        
        if result == QMessageBox.Ok:
            # 实际应用中应该实现更完整的快捷键设置逻辑
            self.tray_icon.showMessage(
                "截图聊天神器", 
                "快捷键设置已保存", 
                QSystemTrayIcon.Information, 
                2000
            )

    def quit_app(self):
        """退出应用程序"""
        self.hotkey.stop()
        self.tray_icon.hide()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tool = ScreenshotTool()
    sys.exit(app.exec())