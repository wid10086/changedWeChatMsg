# WeChatMsg - 微信聊天记录导出与AI分析工具

<div align="center">
    <img src="./doc/images/logo.png" height="120"/>
    <h3>我的数据我做主</h3>
</div>

本项目是从 [quantumopticss/WeChatMsg](https://github.com/quantumopticss/WeChatMsg) ([LC044/WeChatMsg](https://github.com/LC044/WeChatMsg)项目fork而来)项目fork而来，**仅供个人学习和使用**，不用于任何商业目的。在原项目的基础上进行了多项增强，特别是AI聊天功能的改进。

## 🚀 主要特点

- **硅基流动API集成**：替换了原有API，使用硅基流动API进行AI聊天，支持更多高质量模型
- **聊天记录知识库**：AI可读取并利用微信聊天记录作为知识库或前置知识
- **全量聊天记录支持**：优化了导入机制，支持导入大量甚至全部聊天记录
- **智能采样处理**：自动处理大量聊天记录，保留最近500条完整记录，对更早的记录进行智能采样
- **Token限制优化**：解决了token长度超限问题，自动调整聊天记录量以适应不同模型
- **友好的错误处理**：添加了详细的错误提示和处理机制，提高用户体验
- **可配置的API设置**：支持在运行时修改API密钥、模型选择和参数设置

## 💡 增强的AI聊天功能

- **模型选择**：支持多种大型语言模型，包括GLM、Qwen、Baichuan、Yi、InternLM、Llama、Mistral、Claude和GPT系列
- **聊天记录参数设置**：可自定义最大消息数、最大Token数和每条消息估计Token数
- **模型Token限制配置**：提供界面管理不同模型的Token限制，支持添加自定义模型
- **智能聊天记录处理**：根据模型容量自动调整聊天记录的处理方式，确保不超出模型限制
- **上下文保持**：保留对话历史，使AI能够理解对话上下文

## 🔧 原项目保留功能

- **微信数据库解密**：支持解密Windows本地微信数据库
- **聊天界面还原**：还原微信聊天界面，支持文本、图片、系统消息等
- **数据导出**：支持导出为HTML、CSV、TXT、Word等多种格式
- **聊天数据分析**：可视化分析聊天数据，生成年度报告

## 📋 使用方法

1. 下载并运行程序
2. 点击"API设置"按钮配置硅基流动API密钥和模型
3. 点击"聊天记录参数"按钮配置聊天记录处理参数
4. 点击"模型Token限制"按钮配置或查看模型的token限制
5. 点击"聊天记录"按钮选择联系人和是否使用聊天记录作为知识库
6. 开始与AI聊天，享受个性化的对话体验

## ⚠️ 注意事项

- 本项目仅供个人学习和使用，不用于任何商业目的
- 使用聊天记录作为知识库时，请注意保护个人隐私
- 选择"全部"聊天记录时可能因记录过多导致错误，建议适当限制数量
- 所有修改均遵循原项目的开源协议(GPLv3)

## 🙏 致谢

- 原项目：[LC044/WeChatMsg](https://github.com/LC044/WeChatMsg)、[quantumopticss/WeChatMsg](https://github.com/quantumopticss/WeChatMsg)
- 硅基流动API：[Silicon Flow](https://siliconflow.cn/)

## License

WeChatMsg is licensed under [GPLv3](./LICENSE).

Copyright © 2022-2024 by SiYuan.
