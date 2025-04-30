# 截图聊天助手

## 简介
截图聊天助手是一款基于AI的桌面应用程序，允许用户通过快捷键截图并立即获得AI分析结果。该工具特别适合需要快速获取屏幕内容分析的用户。

## 主要功能
- 全局快捷键截图
- 自动分析截图内容
- 将分析结果插入当前光标位置
- 可配置的快捷键和API设置
- 系统托盘图标操作

## 安装指南
1. 克隆本仓库
2. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
3. 激活虚拟环境：
   - Windows：`venv\Scripts\activate`
   - macOS/Linux：`source venv/bin/activate`
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
5. 运行应用：
   ```bash
   python main.py
   ```
## 使用说明
1. 打开截图聊天助手
2. 按下配置的快捷键（默认为`Ctrl+Shift+Q`）
3. 选择要截图的区域
4. 等待AI分析结果
5. 分析结果将自动插入到当前光标位置
## 配置
- 快捷键：在`config.json`文件中修改`hotkey`字段
- API设置：在`config.json`文件中修改`api_key`和`model`字段
- 其他配置项：根据需要修改`config.json`中的其他字段
## 注意事项
- 请确保您的API密钥和模型设置正确
- 请确保您的网络连接正常
- 请确保您的系统支持全局快捷键
## 贡献
欢迎提交Pull Request或Issues :smile:

## 许可证
MIT License