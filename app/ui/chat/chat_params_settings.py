import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QSpinBox,
                            QFormLayout, QGroupBox, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt
from app.config import (save_api_config, load_api_config)

class ChatParamsSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("聊天记录处理参数设置")
        self.resize(550, 300)
        
        # 重新加载最新的配置
        from app.config import load_api_config, CHAT_MAX_MESSAGES, CHAT_MAX_TOKENS, CHAT_ESTIMATED_TOKENS_PER_MSG
        load_api_config()
        
        # 保存配置到实例变量，以便在UI中使用
        self.chat_max_messages = CHAT_MAX_MESSAGES
        self.chat_max_tokens = CHAT_MAX_TOKENS
        self.chat_estimated_tokens_per_msg = CHAT_ESTIMATED_TOKENS_PER_MSG
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 最大消息数
        self.max_messages_input = QSpinBox()
        self.max_messages_input.setRange(100, 10000)
        self.max_messages_input.setSingleStep(100)
        self.max_messages_input.setValue(self.chat_max_messages)
        self.max_messages_input.setToolTip("最多处理的消息数量，超过此数量的较早消息将被忽略")
        form_layout.addRow("最大消息数:", self.max_messages_input)
        
        # 最大token数
        self.max_tokens_input = QSpinBox()
        self.max_tokens_input.setRange(1000, 200000)
        self.max_tokens_input.setSingleStep(1000)
        self.max_tokens_input.setValue(self.chat_max_tokens)
        self.max_tokens_input.setToolTip("用于聊天记录的最大token数，超过此数量将进行智能筛选")
        form_layout.addRow("最大Token数:", self.max_tokens_input)
        
        # 估计每条消息的token数
        self.estimated_tokens_per_msg_input = QSpinBox()
        self.estimated_tokens_per_msg_input.setRange(10, 200)
        self.estimated_tokens_per_msg_input.setSingleStep(5)
        self.estimated_tokens_per_msg_input.setValue(self.chat_estimated_tokens_per_msg)
        self.estimated_tokens_per_msg_input.setToolTip("估计每条消息的平均token数，用于初步筛选")
        form_layout.addRow("估计每条消息Token数:", self.estimated_tokens_per_msg_input)
        
        # 添加表单到主布局
        main_layout.addLayout(form_layout)
        
        # 添加提示信息
        info_label = QLabel("注意: 这些参数用于控制导入到AI的聊天记录数量。如果设置过大可能导致token超限错误。")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(info_label)
        
        # 添加详细说明
        explanation = QLabel(
            "参数说明:\n"
            "- 最大消息数: 限制从数据库加载的消息数量上限\n"
            "- 最大Token数: 限制发送给AI的聊天记录总token数\n"
            "- 估计每条消息Token数: 用于估算消息的token数量\n\n"
            "建议值:\n"
            "- 对于大多数模型: 最大Token数设置为模型上下文窗口的1/3到1/2\n"
            "- 例如: GLM系列可设置为40000-60000, GPT-3.5可设置为4000-6000"
        )
        explanation.setStyleSheet("color: #666; font-size: 10pt;")
        main_layout.addWidget(explanation)
        
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
        
    def save_settings(self):
        """保存设置"""
        chat_max_messages = self.max_messages_input.value()
        chat_max_tokens = self.max_tokens_input.value()
        chat_estimated_tokens_per_msg = self.estimated_tokens_per_msg_input.value()
        
        # 更新配置
        success = save_api_config(
            chat_max_messages=chat_max_messages,
            chat_max_tokens=chat_max_tokens,
            chat_estimated_tokens_per_msg=chat_estimated_tokens_per_msg
        )
        
        if success:
            QMessageBox.information(self, "成功", "聊天记录处理参数已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存聊天记录处理参数失败")
