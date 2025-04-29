import sys
import os
import io
import base64
import pyautogui
import pyperclip
from PySide6.QtWidgets import (QApplication, QSystemTrayIcon,
                               QMenu, QMessageBox, QWidget, QDialog)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, Signal, Slot, QThread
from langchain_community.chat_models import ChatOpenAI
from pynput import keyboard as pynput_keyboard
from config_manager import ConfigManager
from config_dialog import ConfigDialog
import openai

class Worker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, image_data, parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.config_manager = ConfigManager()
        self.prompt = self.config_manager.get('prompt')


    def run(self):
        try:
            client = openai.OpenAI(
                api_key= self.config_manager.get('api_key'),
                base_url=self.config_manager.get('api_base'),
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
                            "text": self.prompt
                        },
                    ],
                }
            ]

            response = client.chat.completions.create(
                model=self.config_manager.get('model'),
                messages=messages,
                max_tokens=1000,
                temperature=0.6,
            )
            
            reply = response.choices[0].message.content
            self.finished.emit(reply)
        except Exception as e:
            self.error.emit(str(e))

class ScreenshotTool(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))

        tray_menu = QMenu()
        
        config_action = QAction("配置", self)
        config_action.triggered.connect(self.show_config_dialog)
        tray_menu.addAction(config_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.shortcut = self.config_manager.get('hotkey')
        self.setup_global_hotkey()


        self.tray_icon.showMessage(
            "截图聊天神器", 
            "程序已启动，使用Ctrl+Alt+Q截图", 
            QSystemTrayIcon.Information, 
            3000
        )

    def setup_global_hotkey(self):
        def on_activate():
            self.capture_and_analyze()
        
        self.hotkey = pynput_keyboard.GlobalHotKeys({
            self.shortcut: on_activate,
        })
        self.hotkey.start()

    def capture_and_analyze(self):
        try:
            screenshot = pyautogui.screenshot()
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
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
        self.tray_icon.showMessage(
            "AI分析错误", 
            error_msg, 
            QSystemTrayIcon.Critical, 
            3000
        )

    def show_config_dialog(self):
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.shortcut = self.config_manager.get('hotkey')
            self.setup_global_hotkey()
            self.tray_icon.showMessage(
                "截图聊天神器", 
                "配置已更新",
                QSystemTrayIcon.Information,
                2000
            )

    def quit_app(self):
        self.hotkey.stop()
        self.tray_icon.hide()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tool = ScreenshotTool()
    sys.exit(app.exec())