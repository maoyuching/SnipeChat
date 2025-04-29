from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                              QLineEdit, QPushButton, QFormLayout, QTextEdit)
from PySide6.QtWidgets import QKeySequenceEdit

class ConfigDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("配置设置")
        self.setMinimumWidth(400)

        form_layout = QFormLayout()

        self.hotkey_input = QKeySequenceEdit()
        current_hotkey = self.config_manager.get('hotkey')
        qkey_sequence = self.convert_to_qkeysequence(current_hotkey)
        self.hotkey_input.setKeySequence(qkey_sequence)

        self.api_base_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.model_input = QLineEdit()
        self.prompt_input = QTextEdit()
        self.knowledge_input = QTextEdit()

        form_layout.addRow("快捷键:", self.hotkey_input)
        form_layout.addRow("API Base URL:", self.api_base_input)
        form_layout.addRow("API Key:", self.api_key_input)
        form_layout.addRow("模型:", self.model_input)
        form_layout.addRow("系统提示词:", self.prompt_input)
        form_layout.addRow("前置知识:", self.knowledge_input)

        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self.save_config)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(btn_save)
        main_layout.addWidget(btn_cancel)

        self.setLayout(main_layout)
        self.load_config()

    def load_config(self):
        config = self.config_manager.config
        self.api_base_input.setText(config.get('api_base', ''))
        self.api_key_input.setText(config.get('api_key', ''))
        self.model_input.setText(config.get('model', ''))
        self.prompt_input.setText(config.get('prompt', ''))
        self.knowledge_input.setText(config.get('knowledge', ''))

    def save_config(self):
        config = {
            'hotkey': self.convert_to_pynput(self.hotkey_input.keySequence()),
            'api_base': self.api_base_input.text(),
            'api_key': self.api_key_input.text(),
            'model': self.model_input.text(),
            'prompt': self.prompt_input.toPlainText(),
            'knowledge': self.knowledge_input.toPlainText()
        }
        self.config_manager.save_config(config)
        self.accept()

    def convert_to_qkeysequence(self, pynput_hotkey):
        return QKeySequence(pynput_hotkey.replace('<', '').replace('>', ''))

    def convert_to_pynput(self, qkey_sequence):
        keys = qkey_sequence.toString().lower().split('+')
        # 处理单个字符的快捷键
        return '+'.join(f'<{key}>' if len(key) > 1 else key for key in keys)