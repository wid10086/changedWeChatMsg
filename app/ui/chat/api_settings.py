import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QMessageBox, QDoubleSpinBox, QSpinBox,
                            QFormLayout, QGroupBox, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QFont, QColor, QPalette
from app.config import (save_api_config, load_api_config)

class ApiSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API设置")
        self.resize(550, 400)

        # 重新加载最新的配置
        from app.config import load_api_config, SIBEI_API_URL, SIBEI_API_KEY, SIBEI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS
        load_api_config()

        # 保存配置到实例变量，以便在UI中使用
        self.api_url = SIBEI_API_URL
        self.api_key = SIBEI_API_KEY
        self.model = SIBEI_MODEL
        self.temperature = AI_TEMPERATURE
        self.max_tokens = AI_MAX_TOKENS

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # API URL
        self.url_input = QLineEdit()
        self.url_input.setText(self.api_url)
        self.url_input.setPlaceholderText("例如: https://api.siliconflow.cn/v1/chat/completions")
        form_layout.addRow("API URL:", self.url_input)

        # API Key
        self.key_input = QLineEdit()
        self.key_input.setText(self.api_key)
        self.key_input.setPlaceholderText("请输入您的API密钥")
        self.key_input.setEchoMode(QLineEdit.Password)  # 密码模式，不显示明文
        form_layout.addRow("API Key:", self.key_input)

        # 模型名称
        self.model_input = QLineEdit()
        self.model_input.setText(self.model)
        self.model_input.setPlaceholderText("例如: THUDM/GLM-Z1-9B-0414")
        form_layout.addRow("模型名称:", self.model_input)

        # 温度参数
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(0.0, 2.0)
        self.temperature_input.setSingleStep(0.1)
        self.temperature_input.setValue(self.temperature)
        self.temperature_input.setToolTip("较低的值使输出更确定，较高的值使输出更随机")
        form_layout.addRow("温度参数:", self.temperature_input)

        # 最大token数
        self.max_tokens_input = QSpinBox()
        self.max_tokens_input.setRange(100, 100000)
        self.max_tokens_input.setSingleStep(100)
        self.max_tokens_input.setValue(self.max_tokens)
        self.max_tokens_input.setToolTip("生成文本的最大长度")
        form_layout.addRow("最大Token数:", self.max_tokens_input)

        # 添加表单到主布局
        main_layout.addLayout(form_layout)

        # 添加提示信息
        info_label = QLabel("注意: 请确保填写正确的API信息，否则AI聊天功能将无法正常工作。")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(info_label)

        # 添加模型提示信息
        model_info = QLabel("常用模型示例:\n"
                           "- THUDM/GLM-Z1-9B-0414\n"
                           "- THUDM/GLM-Z1-32B-0414\n"
                           "- THUDM/GLM-4-9B-Chat\n"
                           "- Qwen/Qwen1.5-7B-Chat\n"
                           "- Qwen/Qwen1.5-14B-Chat\n"
                           "- Baichuan/Baichuan3-Turbo\n"
                           "- meta-llama/llama-3-8b-instruct\n"
                           "- mistralai/mistral-7b-instruct-v0.3\n"
                           "- gpt-4o\n"
                           "- gpt-3.5-turbo")
        model_info.setStyleSheet("color: #666; font-size: 10pt;")
        main_layout.addWidget(model_info)

        # 添加按钮
        button_layout = QHBoxLayout()

        # 创建保存按钮，设置为突出显示
        self.save_button = QPushButton("保存设置")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)

        cancel_button = QPushButton("取消")
        cancel_button.setMinimumHeight(30)

        # 设置按钮布局
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # 连接信号
        self.save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)

        # 添加验证
        self.url_input.textChanged.connect(self.validate_inputs)
        self.key_input.textChanged.connect(self.validate_inputs)
        self.model_input.textChanged.connect(self.validate_inputs)

        # 初始验证
        self.validate_inputs()

    def validate_inputs(self):
        """验证输入是否有效"""
        url = self.url_input.text().strip()
        key = self.key_input.text().strip()
        model = self.model_input.text().strip()

        # 设置URL输入框的样式
        if not url:
            self.url_input.setStyleSheet("border: 1px solid red;")
            self.url_input.setToolTip("API URL不能为空")
        elif not url.startswith(("http://", "https://")):
            self.url_input.setStyleSheet("border: 1px solid orange;")
            self.url_input.setToolTip("API URL应以http://或https://开头")
        else:
            self.url_input.setStyleSheet("")
            self.url_input.setToolTip("")

        # 设置Key输入框的样式
        if not key:
            self.key_input.setStyleSheet("border: 1px solid red;")
            self.key_input.setToolTip("API Key不能为空")
        else:
            self.key_input.setStyleSheet("")
            self.key_input.setToolTip("")

        # 设置模型输入框的样式
        if not model:
            self.model_input.setStyleSheet("border: 1px solid red;")
            self.model_input.setToolTip("模型名称不能为空")
        else:
            self.model_input.setStyleSheet("")
            self.model_input.setToolTip("")

        # 设置保存按钮状态
        self.save_button.setEnabled(bool(url and key and model))

    def save_settings(self):
        """保存设置"""
        url = self.url_input.text().strip()
        key = self.key_input.text().strip()
        model = self.model_input.text().strip()
        temperature = self.temperature_input.value()
        max_tokens = self.max_tokens_input.value()

        # 再次验证
        if not url:
            QMessageBox.warning(self, "警告", "API URL不能为空")
            return

        if not key:
            QMessageBox.warning(self, "警告", "API Key不能为空")
            return

        if not model:
            QMessageBox.warning(self, "警告", "模型名称不能为空")
            return

        # 更新配置
        success = save_api_config(url, key, model, temperature, max_tokens)

        if success:
            QMessageBox.information(self, "成功", "API设置已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存API设置失败")
