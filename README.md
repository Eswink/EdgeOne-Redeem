# EdgeOne-Redeem: EdgeOne 免费计划一键兑换工具

## 项目简介

EdgeOne-Redeem 是一个用于自动兑换 EdgeOne 免费计划的工具，支持图形界面和命令行两种使用方式。它可以帮助用户快速登录 EdgeOne 平台，获取必要的认证信息，并批量兑换免费计划的兑换码，简化兑换流程，提高效率。

## 功能特点

- 自动登录 EdgeOne 平台并获取认证信息
- 支持批量兑换 EdgeOne 兑换码
- 图形界面 (GUI) 和命令行 (CLI) 两种使用方式
- 实时显示兑换状态和日志信息
- 支持并发兑换，提高兑换效率
- 完全开源，遵循 MIT 许可证

## 安装要求

### 系统要求

- Windows、macOS 或 Linux 操作系统
- Python 3.9 或更高版本

### 依赖安装

```bash
# 安装 Python 依赖
pip install selenium selenium-stealth requests
```

### 浏览器和驱动要求

- Google Chrome 浏览器 (最新版本)
- 对应版本的 chromedriver：
  - [Windows 下载](https://chromedriver.chromium.org/downloads)
  - [macOS 下载](https://chromedriver.chromium.org/downloads)
  - [Linux 下载](https://chromedriver.chromium.org/downloads)
  
**注意：** 请将 chromedriver 路径添加到系统环境变量中，确保程序可以找到它。

## 使用方法

### GUI 图形界面使用方法

1. 运行图形界面程序：
   ```bash
   python edgeone_gui_redeem.py
   ```

2. 在打开的窗口中：
   - 在左侧文本框中输入需要兑换的兑换码（每行一个）
   - 点击"获取登录信息"按钮，系统将自动打开浏览器，需要用户手动进行登录
   - 登录完成后，浏览器会自动关闭，程序会获取必要的认证信息
   - 点击"一键兑换"按钮，开始批量兑换输入的兑换码
   - 查看右侧状态显示和下方日志框，获取兑换进度和结果

### CLI 命令行使用方法

1. 运行命令行程序并指定兑换码：
   ```bash
   python edgeone_redeem.py YOUR_REDEEM_CODE
   ```

2. 系统将自动打开浏览器进行登录，完成后会显示兑换结果：
   ```json
   {
     "code": 0,
     "message": "操作成功",
     "data": {
       "code": "兑换码状态",
       "message": "兑换结果说明",
       // 其他相关数据
     }
   }
   ```

## 项目结构

```
EdgeOne-Redeem/
├── edgeone_gui_redeem.py  # 图形界面版本主程序
├── edgeone_redeem.py     # 命令行版本主程序
└── README.md             # 项目说明文档
```

### 主要模块功能

- `get_skey_and_uin`: 使用 Selenium 打开登录页，获取 skey 和 uin 信息
- `call_token_api`: 使用获取的 skey 和 uin 调用 token 接口，获取兑换所需的 key 和 ownerUin
- `redeem_code`: 执行兑换码兑换操作
- `djb2_hash`: 计算 x-csrfcode，用于请求认证
- `on_get_token`: GUI 版本中获取登录信息的按钮逻辑
- `on_redeem_all`: GUI 版本中一键兑换的按钮逻辑

## 注意事项

1. 首次使用时，浏览器会打开登录页面，请使用你的 Tencent Cloud 账号登录
2. 请确保 chromedriver 版本与你的 Chrome 浏览器版本匹配
3. 批量兑换时，程序会自动控制并发数量（最多 5 个并发）
4. 兑换结果将显示在日志框中，包括兑换码状态和详细信息
5. 如果登录或兑换过程中出现错误，请查看日志信息以获取详细错误描述

## 免责声明

- 本工具仅供学习和个人使用，严禁用于任何商业或非法用途
- 请遵守 EdgeOne 和 Tencent Cloud 的服务条款和使用政策
- 作者不对因使用本工具而导致的任何直接或间接损失负责
- 本工具可能因平台策略变更而失效，作者会尽力维护但不保证永久可用

## 开源许可证

本项目遵循 MIT 开源许可证，详情请查看 [LICENSE](LICENSE) 文件。

## 关于作者

- 作者：Eswlnk Blog
- 博客：https://blog.eswlnk.com
- 本工具已开源，欢迎提交 issue 和 pull request 进行改进

如果在使用过程中遇到问题，或者有任何建议，欢迎通过博客或项目仓库与我联系。
