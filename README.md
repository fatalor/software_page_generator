# 📱 软件页面生成器

> 一个自动化生成软件介绍页面的高效工具，专为技术博主、软件开发者设计

![版本](https://img.shields.io/badge/版本-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![开源协议](https://img.shields.io/badge/开源协议-MIT-yellow)

## ✨ 项目简介

**软件页面生成器** 是一个高效的自动化工具，能够根据配置文件快速生成专业的软件介绍页面。特别适合技术博主、软件分享者使用，可以大大节省编写重复内容的时间。

### 🌟 核心特性

- 🚀 **一键生成**：从配置文件到完整页面，一键完成
- 🖼️ **图片自动上传**：拖放图片自动上传到图床并获取URL
- 📝 **多格式输出**：同时生成纯HTML、WordPress格式、预览页面
- ⚡ **批量处理**：支持多个配置文件批量生成
- 🎨 **模板化设计**：灵活的模板系统，易于定制
- 🔧 **简单配置**：使用简单的INI格式配置文件

## 📁 项目结构

```
software_page_generator/
├── 📂 configs/                 # 配置文件目录
├── 📂 templates/               # 模板文件目录
├── 📂 resources/               # 图片资源目录
│   ├── to_upload/             # 待上传图片
│   └── uploaded/              # 已上传图片和URL
├── 📂 output/                  # 生成的HTML内容
├── 📂 previews/                # 预览页面
├── 📂 contents/                # WordPress格式内容
├── 📜 build.py                 # 主构建脚本
├── 📜 upload_images.py         # 图片上传工具
├── 📜 requirements.txt         # 依赖列表
└── 📜 README.md               # 说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <项目地址>

# 安装依赖
pip install -r requirements.txt

# Windows用户可选安装剪贴板支持
pip install pillow pywin32
```

### 2. 配置PicGo（可选）

如果你需要自动上传图片功能，请先安装并配置 [PicGo](https://github.com/Molunerfinn/PicGo)：

1. 下载安装PicGo
2. 配置图床（推荐：GitHub、SM.MS、阿里云OSS等）
3. 确保PicGo正常运行

### 3. 创建配置文件

在 `configs/` 目录下创建 `.info` 文件，例如 `my_software.info`：

```ini
[软件信息]
标题 = 我的软件名称
名称 = 软件完整名称
版本 = 1.0.0
描述 = 这是一个非常棒的软件...

[功能介绍]
1 = 功能一描述
2 = 功能二描述

[软件截图]
1 = 截图标题|来源说明|图片URL

[下载链接]
https://example.com/download1
https://example.com/download2 提取码
```

### 4. 上传图片（可选）

```bash
# 启动图片上传工具
python upload_images.py

# 选择模式2（监控模式）
# 将图片拖放到 resources/to_upload/ 目录
# 自动上传并复制URL到剪贴板
```

### 5. 生成页面

```bash
# 生成所有页面
python build.py

# 或生成单个配置
python build.py gen my_software

# 查看配置列表
python build.py list
```

## 📋 详细使用说明

### 配置文件格式说明

#### `[软件信息]` 节
- **标题**：用于生成文件名，如 `{标题}.html`
- **名称**：页面显示的软件名称
- **版本**：软件版本号
- **描述**：软件详细介绍，支持多段文本（用`||`分隔）

#### `[功能介绍]` 节
- 每行一个功能描述
- 支持编号格式或直接列表

#### `[软件截图]` 节
- 格式：`编号 = 标题|来源|图片URL`
- 示例：`1 = 软件主界面|© 纯净工具站|https://puretool.cn/image.png`

#### `[下载链接]` 节
- 每行一个下载链接
- 可选添加提取码：`URL 提取码`

### 图片上传功能

图片上传工具提供两种模式：

1. **监控模式**：实时监控目录，拖放即上传
2. **批量模式**：一次性处理所有待上传图片

上传后会自动：
- 复制URL到剪贴板
- 移动图片到已上传目录
- 保存URL记录

### 生成的文件说明

运行 `build.py` 后会生成三类文件：

1. **`output/`**：纯HTML内容文件，仅包含内容标签
2. **`previews/`**：完整HTML预览文件，可浏览器查看
3. **`contents/`**：WordPress短代码格式内容

## 🔧 命令行工具

### `build.py` 命令

| 命令 | 说明 |
|------|------|
| `python build.py` | 生成所有配置文件的HTML页面 |
| `python build.py list` | 列出所有配置文件 |
| `python build.py gen <名称>` | 生成单个配置文件页面 |
| `python build.py clean` | 清理所有生成的文件 |
| `python build.py help` | 显示帮助信息 |

### `upload_images.py` 命令

直接运行 `python upload_images.py`，然后选择：
1. 处理现有图片
2. 启动监控模式（推荐）
3. 显示帮助信息

## 🎯 使用场景

### 场景一：技术博主分享软件
1. 创建软件配置文件
2. 上传软件截图
3. 生成页面并发布到博客

### 场景二：软件开发者发布更新
1. 更新版本号和描述
2. 上传新版截图
3. 生成更新日志页面

### 场景三：资源整理分享
1. 整理多个软件配置
2. 批量生成页面
3. 建立软件资源站

## ⚙️ 高级定制

### 修改模板

编辑 `templates/page_template.py` 中的 `generate_wordpress_content` 函数，可以自定义输出格式。

### 样式定制

生成的预览页面包含CSS样式，可以直接修改 `generate_html_embed` 函数中的CSS部分。

### 扩展功能

项目采用模块化设计，可以轻松扩展：
- 添加新的输出格式
- 集成其他图床服务
- 添加统计分析功能


## 📄 开源协议

本项目采用 MIT 协议开源。详见 [LICENSE](LICENSE) 文件。

## 👤 作者信息

**纯净工具站** - 专注于提供纯净、高效的软件工具

- 🌐 官方网站：[https://www.puretool.cn](https://www.puretool.cn)
- 📧 联系邮箱：leicongdoc@163.com
- 🐧 腾讯QQ：820254639
- 🎬 Bilibili：[https://space.bilibili.com/382770100](https://space.bilibili.com/382770100)

## 🙏 致谢

感谢以下开源项目和技术的贡献：

- [DeepSeek](https://www.deepseek.com/) - 本项目在DeepSeek AI助手的帮助下完成开发，提供了宝贵的技术指导和代码实现建议
- [PicGo](https://github.com/Molunerfinn/PicGo) - 优秀的图床工具，为本项目的图片上传功能提供了核心支持
- Python社区 - 丰富的开源库和文档资源
---

<div align="center">
  
**如果这个项目对你有帮助，请点个 ⭐ Star 支持一下！**

🎉 **让分享变得更简单，让创作变得更高效** 🎉

</div>