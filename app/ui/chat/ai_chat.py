import json
import sys
import time
import traceback
import re

import requests
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication, QTextBrowser, QMessageBox, QPushButton

from app import config
from app.log import logger
from app.ui.Icon import Icon

try:
    from .chatInfoUi import Ui_Form
except:
    from chatInfoUi import Ui_Form
from app.components.bubble_message import BubbleMessage
from app.person import Me, ContactDefault


class Message(QWidget):
    def __init__(self, is_send=False, text='', parent=None):
        super().__init__(parent)
        self.avatar = QLabel(self)

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setText(text)

        layout = QHBoxLayout(self)
        if is_send:
            pixmap = Me().avatar.scaled(45, 45)
            self.textBrowser.setLayoutDirection(Qt.RightToLeft)
            self.textBrowser.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.avatar.setPixmap(pixmap)
            layout.addWidget(self.textBrowser)
            layout.addWidget(self.avatar)
        else:
            pixmap = QPixmap(Icon.Default_avatar_path).scaled(45, 45)
            self.avatar.setPixmap(pixmap)
            layout.addWidget(self.avatar)
            layout.addWidget(self.textBrowser)
        # self.textBrowser.setFixedHeight(int(self.textBrowser.document().size().height()))
        self.textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.avatar.setFixedSize(QSize(60, 60))

    def append(self, text: str):
        self.textBrowser.insertPlainText(text)
        self.textBrowser.setFixedHeight(int(self.textBrowser.document().size().height()))


class AIChat(QWidget, Ui_Form):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.now_message: Message = None
        self.setupUi(self)
        self.last_timestamp = 0
        self.last_str_time = ''
        self.last_pos = 0
        self.contact = contact
        self.init_ui()
        self.show_chats()
        self.pushButton.clicked.connect(self.send_msg)
        self.toolButton.clicked.connect(self.tool)
        self.toolButton.setText("聊天记录")  # 修改工具按钮文本
        self.btn_clear.clicked.connect(self.clear_dialog)
        self.btn_clear.setIcon(Icon.Clear_Icon)

        # 添加API设置按钮 - 使用更显眼的样式
        self.api_button = QPushButton("API设置")
        self.api_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 10px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.horizontalLayout_2.addWidget(self.api_button)
        self.api_button.clicked.connect(self.show_api_settings)

        # 添加聊天记录参数设置按钮
        self.chat_params_button = QPushButton("聊天记录参数")
        self.chat_params_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 10px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6fc2;
            }
        """)
        self.horizontalLayout_2.addWidget(self.chat_params_button)
        self.chat_params_button.clicked.connect(self.show_chat_params_settings)

    def init_ui(self):
        self.textEdit.installEventFilter(self)

    def show_api_settings(self):
        """显示API设置对话框"""
        from app.ui.chat.api_settings import ApiSettingsDialog
        from app.config import load_api_config

        dialog = ApiSettingsDialog(self)
        if dialog.exec_():
            # 立即重新加载配置，使设置立即生效
            load_api_config()

            # 通知用户设置已更新并立即生效
            QMessageBox.information(self, "设置已保存", "API设置已更新并立即生效，无需重启应用。")

    def show_chat_params_settings(self):
        """显示聊天记录参数设置对话框"""
        from app.ui.chat.chat_params_settings import ChatParamsSettingsDialog
        from app.config import load_api_config

        dialog = ChatParamsSettingsDialog(self)
        if dialog.exec_():
            # 立即重新加载配置，使设置立即生效
            load_api_config()

            # 通知用户设置已更新并立即生效
            QMessageBox.information(self, "设置已保存", "聊天记录处理参数已更新并立即生效，无需重启应用。")

    def tool(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton
        from app.DataBase import micro_msg_db, msg_db

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("聊天记录设置")
        dialog.resize(400, 200)

        # 创建布局
        layout = QVBoxLayout()

        # 添加联系人选择
        contact_layout = QHBoxLayout()
        contact_label = QLabel("选择联系人:")
        contact_combo = QComboBox()

        # 获取联系人列表
        contacts = micro_msg_db.get_contact()
        contact_dict = {}

        # 添加联系人到下拉框
        for contact_info in contacts:
            if contact_info and len(contact_info) >= 5:
                wxid = contact_info[0]
                nickname = contact_info[4] or wxid
                remark = contact_info[3] or nickname
                display_name = remark or nickname
                contact_dict[display_name] = wxid
                contact_combo.addItem(display_name)

        contact_layout.addWidget(contact_label)
        contact_layout.addWidget(contact_combo)

        # 添加是否启用聊天记录作为知识库的选项
        use_history_checkbox = QCheckBox("使用聊天记录作为知识库或前置知识（选择'全部'时可能会因记录过多导致错误）")

        # 添加消息数量限制选项
        limit_layout = QHBoxLayout()
        limit_label = QLabel("加载消息数量限制:")
        limit_combo = QComboBox()
        for limit in [50, 100, 500, 1000, 2000, 5000, "全部"]:
            limit_combo.addItem(str(limit))
        limit_combo.setCurrentText("50")  # 默认50条
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(limit_combo)

        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 添加到主布局
        layout.addLayout(contact_layout)
        layout.addWidget(use_history_checkbox)
        layout.addLayout(limit_layout)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        # 连接信号
        def on_ok():
            selected_contact = contact_combo.currentText()
            wxid = contact_dict.get(selected_contact)
            use_history = use_history_checkbox.isChecked()
            limit_text = limit_combo.currentText()

            # 处理"全部"选项
            if limit_text == "全部":
                limit = None  # None表示不限制数量
            else:
                limit = int(limit_text)

            if wxid:
                self.show_chat_thread.contact_wxid = wxid
                self.show_chat_thread.use_chat_history = use_history
                self.show_chat_thread.load_chat_history(wxid, limit)

                if use_history:
                    limit_display = f"最近 {limit} 条" if limit else "全部"
                    QMessageBox.information(self, "设置成功", f"已成功加载联系人 {selected_contact} 的{limit_display}聊天记录作为知识库")
                else:
                    QMessageBox.information(self, "设置成功", f"已选择联系人 {selected_contact}，但未启用聊天记录作为知识库")

            dialog.accept()

        def on_cancel():
            dialog.reject()

        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)

        # 显示对话框
        dialog.exec_()

    def chat(self, text):
        self.now_message.append(text)
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())

    def send_msg(self):
        msg = self.textEdit.toPlainText().strip()
        self.textEdit.setText('')
        if not msg:
            return
        print(msg)
        bubble_message = BubbleMessage(
            msg,
            Me().avatar,
            1,
            True,
        )
        self.verticalLayout_message.addWidget(bubble_message)
        message1 = Message(False)
        self.verticalLayout_message.addWidget(message1)
        self.show_chat_thread.msg = msg
        self.now_message = message1
        self.show_chat_thread.start()
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())

    def clear_dialog(self):
        self.show_chat_thread.history = []
        while self.verticalLayout_message.count():
            item = self.verticalLayout_message.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                del item

    def show_chats(self):
        # return
        self.show_chat_thread = AIChatThread()
        self.show_chat_thread.msgSignal.connect(self.chat)

    def update_history_messages(self):
        print('开始发送信息')
        message1 = Message(False)
        msg = '你好！'
        self.verticalLayout_message.addWidget(message1)
        self.show_chat_thread.msg = msg
        self.now_message = message1
        self.show_chat_thread.start()

    def add_message(self, message):
        print('message', message)
        # self.textBrowser.append(message)
        self.textBrowser.insertPlainText(message)
        self.textBrowser.setFixedHeight(int(self.textBrowser.document().size().height()))

    def eventFilter(self, obj, event):
        if obj == self.textEdit and event.type() == event.KeyPress:
            key = event.key()
            if key == 16777220:  # 回车键的键值
                self.send_msg()
                self.textEdit.setText('')
                return True
        return super().eventFilter(obj, event)


class AIChatThread(QThread):
    msgSignal = pyqtSignal(str)
    showSingal = pyqtSignal(tuple)
    finishSingal = pyqtSignal(int)
    msg_id = 0

    # heightSingal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.msg = ''
        self.history = []
        self.chat_history = []  # 存储从数据库加载的聊天记录
        self.contact_wxid = None  # 联系人wxid
        self.use_chat_history = False  # 是否使用聊天记录作为知识库

    def get_model_max_tokens(self, model_name):
        """
        根据模型名称获取最大token限制
        @param model_name: 模型名称
        @return: 最大token限制
        """
        # 不同模型的最大token限制
        model_limits = {
            # GLM系列
            "THUDM/GLM-Z1-9B-0414": 32768,
            "THUDM/GLM-Z1-32B-0414": 131072,
            "THUDM/GLM-Z1-64B-0414": 131072,
            "THUDM/GLM-4-9B-Chat": 32768,
            "THUDM/GLM-4-32B-Chat": 131072,
            "THUDM/GLM-4-64B-Chat": 131072,

            # Qwen系列
            "Qwen/Qwen1.5-7B-Chat": 32768,
            "Qwen/Qwen1.5-14B-Chat": 32768,
            "Qwen/Qwen1.5-32B-Chat": 32768,
            "Qwen/Qwen1.5-72B-Chat": 32768,
            "Qwen/Qwen2-7B-Instruct": 32768,
            "Qwen/Qwen2-57B-Instruct": 32768,

            # Baichuan系列
            "Baichuan/Baichuan3-Turbo": 16384,
            "Baichuan/Baichuan3-Plus": 16384,
            "Baichuan/Baichuan3-Pro": 16384,

            # Yi系列
            "01-ai/Yi-1.5-9B-Chat": 4096,
            "01-ai/Yi-1.5-34B-Chat": 4096,
            "01-ai/Yi-2.0-9B-Chat": 4096,
            "01-ai/Yi-2.0-34B-Chat": 4096,

            # InternLM系列
            "internlm/internlm2-chat-7b": 8192,
            "internlm/internlm2-chat-20b": 8192,
            "internlm/internlm2-chat-110b": 8192,

            # Moonshot系列
            "moonshot/moonshot-v1-8k": 8192,
            "moonshot/moonshot-v1-32k": 32768,
            "moonshot/moonshot-v1-128k": 131072,

            # DeepSeek系列
            "deepseek/deepseek-chat": 8192,
            "deepseek/deepseek-coder": 16384,

            # Llama系列
            "meta-llama/llama-3-8b-instruct": 8192,
            "meta-llama/llama-3-70b-instruct": 8192,
            "meta-llama/llama-3-8b-instruct-4k": 4096,
            "meta-llama/llama-3-70b-instruct-4k": 4096,
            "meta-llama/llama-3-8b-instruct-8k": 8192,
            "meta-llama/llama-3-70b-instruct-8k": 8192,
            "meta-llama/llama-3-8b-instruct-32k": 32768,
            "meta-llama/llama-3-70b-instruct-32k": 32768,
            "meta-llama/llama-3-8b-instruct-128k": 131072,
            "meta-llama/llama-3-70b-instruct-128k": 131072,

            # Mistral系列
            "mistralai/mistral-7b-instruct-v0.3": 8192,
            "mistralai/mistral-large-latest": 32768,
            "mistralai/mixtral-8x7b-instruct-v0.1": 32768,
            "mistralai/mixtral-8x22b-instruct-v0.1": 32768,

            # Claude系列
            "anthropic/claude-3-opus-20240229": 200000,
            "anthropic/claude-3-sonnet-20240229": 200000,
            "anthropic/claude-3-haiku-20240307": 200000,
            "anthropic/claude-3.5-sonnet-20240620": 200000,

            # GPT系列
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-2024-04-09": 128000,
            "gpt-4-vision-preview": 128000,
            "gpt-4-1106-preview": 128000,
            "gpt-4-0125-preview": 128000,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 16384,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-1106": 16384,
            "gpt-3.5-turbo-0125": 16384,
        }

        # 如果找到模型，返回其限制，否则返回默认值
        if model_name in model_limits:
            return model_limits[model_name]

        # 对于未知模型，根据名称中的关键字猜测
        if "32k" in model_name.lower():
            return 32768
        elif "16k" in model_name.lower():
            return 16384
        elif "8k" in model_name.lower():
            return 8192
        elif "4k" in model_name.lower():
            return 4096
        elif "128k" in model_name.lower():
            return 131072

        # 默认返回一个保守的值
        return 8192  # 默认为8K上下文窗口

    def load_chat_history(self, wxid, limit=50):
        """
        加载指定联系人的聊天记录
        @param wxid: 联系人wxid
        @param limit: 加载的消息数量限制，None表示不限制
        """
        from app.DataBase import msg_db
        if not wxid:
            return

        self.contact_wxid = wxid
        # 获取最近的聊天记录
        messages = msg_db.get_messages(wxid)
        if not messages:
            return

        # 只保留文本消息
        text_messages = [msg for msg in messages if msg[2] == 1]  # type=1 表示文本消息

        # 如果有限制，则只保留最近的消息
        if limit is not None and len(text_messages) > limit:
            text_messages = text_messages[-limit:]

        self.chat_history = text_messages

    def run(self) -> None:
        # 从配置文件重新加载最新的API配置
        from app.config import load_api_config, SIBEI_API_URL, SIBEI_API_KEY, SIBEI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS

        # 重新加载配置，确保使用最新的设置
        load_api_config()

        # 检查API配置是否完整
        if not SIBEI_API_KEY:
            self.msgSignal.emit("错误: API密钥未设置，请点击界面上的'API设置'按钮配置您的API密钥。")
            return

        if not SIBEI_MODEL:
            self.msgSignal.emit("错误: 模型名称未设置，请点击界面上的'API设置'按钮配置模型名称。")
            return

        # 使用配置文件中的硅基流动API地址
        url = SIBEI_API_URL

        # 构建硅基流动API请求格式
        messages = []

        # 如果启用了聊天记录作为知识库，添加系统提示和聊天记录
        if self.use_chat_history and self.chat_history:
            # 添加系统提示，告诉AI这是聊天记录
            messages.append({
                'role': 'system',
                'content': f'以下是与联系人的历史聊天记录，请将其作为知识库或前置知识来回答用户的问题。'
            })

            # 将聊天记录转换为消息格式，使用更智能的方法处理大量聊天记录

            # 从配置文件获取聊天记录处理参数
            from app.config import CHAT_MAX_MESSAGES, CHAT_MAX_TOKENS, CHAT_ESTIMATED_TOKENS_PER_MSG

            # 获取模型的最大token限制
            model_max_tokens = self.get_model_max_tokens(SIBEI_MODEL)

            # 为其他内容预留一些token（如系统提示、当前问题等）
            reserved_tokens = 3000

            # 计算可用于聊天记录的最大token数
            # 使用配置文件中的CHAT_MAX_TOKENS和模型限制中的较小值
            available_tokens = min(CHAT_MAX_TOKENS, model_max_tokens - reserved_tokens)

            # 使用配置文件中的参数
            max_messages = CHAT_MAX_MESSAGES
            max_tokens = available_tokens

            # 如果消息太多，只取最近的部分消息
            processed_messages = self.chat_history
            if len(processed_messages) > max_messages:
                processed_messages = processed_messages[-max_messages:]

            # 估计每条消息的token数
            estimated_tokens_per_msg = CHAT_ESTIMATED_TOKENS_PER_MSG

            # 首先添加最近的100条消息（这些是最重要的）
            recent_messages = processed_messages[-100:] if len(processed_messages) > 100 else processed_messages
            recent_chunk = []

            for msg in recent_messages:
                sender = "对方" if msg[4] == 0 else "我"
                content = msg[7]
                time_str = msg[8]
                formatted_msg = f"{time_str} {sender}: {content}\n"
                recent_chunk.append(formatted_msg)

            # 然后处理剩余的消息
            remaining_messages = processed_messages[:-100] if len(processed_messages) > 100 else []

            # 计算剩余token预算
            recent_tokens = len(recent_messages) * estimated_tokens_per_msg
            remaining_tokens = max_tokens - recent_tokens

            # 如果剩余消息太多，采样处理
            if len(remaining_messages) > 0:
                # 计算采样率
                sample_rate = min(1.0, remaining_tokens / (len(remaining_messages) * estimated_tokens_per_msg))

                if sample_rate < 1.0:
                    # 采样处理，保留重要的消息
                    sampled_messages = []
                    step = max(1, int(1 / sample_rate))

                    # 每隔step条消息取一条
                    for i in range(0, len(remaining_messages), step):
                        sampled_messages.append(remaining_messages[i])

                    remaining_messages = sampled_messages

            # 处理剩余消息
            remaining_chunk = []
            for msg in remaining_messages:
                sender = "对方" if msg[4] == 0 else "我"
                content = msg[7]
                time_str = msg[8]
                formatted_msg = f"{time_str} {sender}: {content}\n"
                remaining_chunk.append(formatted_msg)

            # 组合所有内容
            chat_content = ""

            # 添加提示信息
            if len(self.chat_history) > max_messages:
                chat_content += f"[注意：聊天记录过多，只显示部分重要消息，共{len(processed_messages)}条]\n\n"

            # 先添加较早的消息（如果有采样，会说明）
            if remaining_chunk:
                if len(remaining_messages) < len(processed_messages) - 100:
                    chat_content += f"[以下是采样的较早聊天记录，每隔一段时间选取一条，共{len(remaining_messages)}条]\n"
                chat_content += "".join(remaining_chunk)
                chat_content += "\n[以下是最近的聊天记录，按时间顺序排列]\n"

            # 再添加最近的消息
            chat_content += "".join(recent_chunk)

            # 添加聊天记录作为系统消息
            messages.append({
                'role': 'system',
                'content': f'聊天记录内容如下:\n{chat_content}\n请根据以上聊天记录回答用户的问题。'
            })

        # 添加历史对话
        for msg in self.history:
            messages.append(msg)

        # 添加当前用户消息
        messages.append({
            'role': 'user',
            'content': self.msg
        })

        # 使用最新的配置参数
        data = {
            'model': SIBEI_MODEL,
            'messages': messages,
            'stream': True,
            'temperature': AI_TEMPERATURE,
            'max_tokens': AI_MAX_TOKENS
        }

        # 添加API密钥到请求头
        headers = {
            'Authorization': f'Bearer {SIBEI_API_KEY}',
            'Content-Type': 'application/json'
        }

        try:
            resp = requests.post(url, json=data, headers=headers, stream=True)

            message = {
                'role': 'user',
                'content': self.msg
            }

            resp_message = {
                'role': 'assistant',
                'content': ''
            }

            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            if line_text == 'data: [DONE]':
                                continue

                            try:
                                json_str = line_text[6:]  # 去掉 'data: ' 前缀
                                data = json.loads(json_str)

                                # 解析硅基流动API的响应格式
                                if 'choices' in data and len(data['choices']) > 0:
                                    choice = data['choices'][0]
                                    if 'delta' in choice and 'content' in choice['delta'] and choice['delta']['content']:
                                        content = choice['delta']['content']
                                        resp_message['content'] += content
                                        self.msgSignal.emit(content)
                            except Exception as e:
                                print(f"解析响应出错: {e}")
                                print(f"原始数据: {line_text}")
                                if 'data: ' not in line_text:
                                    self.msgSignal.emit(line_text)
            else:
                print(resp.text)
                try:
                    error_data = resp.json()
                    # 处理不同格式的错误响应
                    if 'error' in error_data and isinstance(error_data['error'], dict):
                        error_msg = error_data['error'].get('message', '未知错误')
                    elif 'message' in error_data:
                        error_msg = error_data['message']
                    else:
                        error_msg = str(error_data)

                    logger.error(f'AI请求错误: {error_msg}')

                    # 提供更友好的错误信息
                    if "length of prompt_tokens" in error_msg and "must be less than max_seq_len" in error_msg:
                        # 提取实际的token数量和限制
                        import re
                        token_match = re.search(r'length of prompt_tokens \((\d+)\) must be less than max_seq_len \((\d+)\)', error_msg)
                        if token_match:
                            actual_tokens = int(token_match.group(1))
                            max_seq_len = int(token_match.group(2))

                            # 构建更详细的错误信息
                            error_detail = (
                                f"错误: 聊天记录太长，超出了模型的处理能力。\n"
                                f"当前token数: {actual_tokens}, 模型限制: {max_seq_len}\n"
                                f"请通过以下方式解决:\n"
                                f"1. 点击'聊天记录参数'按钮，减小'最大Token数'(建议设置为{max_seq_len//2})\n"
                                f"2. 减少加载的聊天记录数量\n"
                                f"3. 选择不使用聊天记录作为知识库"
                            )
                            self.msgSignal.emit(error_detail)
                        else:
                            self.msgSignal.emit(f"错误: 聊天记录太长，超出了模型的处理能力。请减少加载的聊天记录数量，或者选择不使用聊天记录作为知识库。")
                    else:
                        self.msgSignal.emit(f"错误: {error_msg}")
                except:
                    logger.error(f'AI请求错误: HTTP状态码 {resp.status_code}')
                    self.msgSignal.emit(f"错误: HTTP状态码 {resp.status_code}")

            # 保存对话历史
            self.history.append(message)
            self.history.append(resp_message)
        except Exception as e:
            error = str(e)
            logger.error(f'AI请求错误: {error}\n{traceback.format_exc()}')
            self.msgSignal.emit(f"连接错误: {error}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    contact = ContactDefault('1')
    dialog = AIChat(contact)
    dialog.show()
    sys.exit(app.exec_())
