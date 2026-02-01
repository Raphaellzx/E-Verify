# 网页核查自动化项目

## 项目概述

Everify（E-Verify）是一个网页核查自动化工具，用于自动访问指定网页查询主体信息并生成带有时间水印的Word报告。该项目支持自动核查和人工核查相结合的方式，提高了核查效率和报告质量。

## 功能特点

### 核心功能
1. **自动核查**：自动访问预配置的网页，搜索指定主体的信息并截图
2. **报告生成**：自动生成格式规范的Word报告，包含时间水印
3. **人工核查**：支持插入人工核查的截图，补充自动核查的内容
4. **菜单式操作**：提供直观的菜单系统，用户可以选择操作流程

### 优化后的流程
1. **输入主体信息**：程序启动时先获取需要核查的主体列表
2. **选择操作**：
   - 选项1：进行自动核查部分（自动访问网页、截图、生成报告）
   - 选项2：插入人工核查图片（为已生成的报告插入人工截图）
   - 选项3：退出程序
3. **循环操作**：完成任务后重新显示菜单，直到用户选择退出

### 技术特点
1. **异步执行**：使用 asyncio + Playwright 实现高效的网页访问
2. **模板驱动**：通过配置文件定义需要核查的网页模板
3. **智能截图**：自动计算截图索引，支持多种截图组织方式
4. **报告格式**：生成符合规范的Word文档，包含水印和章节编号

## 安装与配置

### 环境要求
- Python 3.10.19 或更高版本
- uv 包管理器（用于依赖管理）

### 安装依赖
```bash
cd "d:\Coding\Python\Everify-project"
uv pip install -r requirements.txt
# 或者使用 uv sync 同步依赖
uv sync
```

### 浏览器驱动安装
Playwright 需要安装浏览器驱动：
```bash
uv run python -m playwright install
```

## 使用方法

### 命令行运行
```bash
cd "d:\Coding\Python\Everify-project"
uv run everify
```

### 选项说明
```
-c, --config      配置文件路径
-o, --output      输出目录
-t, --templates   模板文件路径
-v, --verbose     显示详细日志
-e, --entities    主体列表文件路径（批量模式）
-s, --screenshots-dir 截图保存目录
```

### 操作流程

1. **运行程序**：
   ```bash
   uv run everify
   ```

2. **输入主体信息**：
   - 逐个输入需要核查的主体名称（每行一个）
   - 输入 `#` 停止输入

3. **选择操作**：
   ```
   ------------------------------------------
   请选择操作：
   1. 进行自动核查部分
      - 自动访问网页
      - 截取网页截图
      - 生成包含自动化截图的报告
   2. 插入人工核查图片
      - 为已生成的报告插入人工核查的截图
   3. 退出程序
   ------------------------------------------
   请输入您的选择 (1-3):
   ```

### 批量模式

如果有大量主体需要核查，可以使用批量模式：

1. 创建一个包含主体列表的文本文件（每行一个主体）：
   ```text
   # entities.txt
   晋能控股集团有限公司
   晋能控股煤业集团有限公司
   山西焦煤集团有限责任公司
   西山煤电（集团）有限责任公司
   晋能控股装备制造集团有限公司
   ```

2. 使用 `-e` 选项运行程序：
   ```bash
   uv run everify -e entities.txt
   ```

## 项目结构

```
Everify-project/
├── src/everify/              # 主源代码目录
│   ├── main.py              # 程序入口
│   ├── core/                # 核心功能模块
│   │   ├── services/        # 业务逻辑层
│   │   │   ├── entity_manager.py        # 主体管理
│   │   │   ├── template_manager.py      # 模板管理
│   │   │   ├── url_generator.py         # URL生成
│   │   │   ├── verify_service.py        # 核查服务
│   │   │   └── report_generator.py      # 报告生成
│   │   ├── base/            # 基础功能实现
│   │   │   ├── browser.py   # 浏览器引擎（Playwright）
│   │   │   ├── document.py  # 文档引擎（python-docx）
│   │   │   └── image.py     # 图片引擎（Pillow）
│   │   └── utils/           # 工具模块
│   │       ├── config.py    # 配置管理
│   │       └── logger.py    # 日志工具
│   └── utils/               # 通用工具
│       └── file.py          # 文件操作工具
├── tests/                   # 测试用例
├── output/                  # 输出目录（运行时自动创建）
│   ├── reports/             # 生成的报告
│   ├── screenshots/         # 截图文件
│   ├── temp/                # 临时文件
│   └── logs/                # 日志文件
├── templates.json           # 网页核查模板
├── pyproject.toml           # 项目配置
├── uv.lock                  # uv依赖锁定文件
└── .gitignore               # Git忽略配置
```

## 配置文件

### 核查模板（templates.json）
定义需要核查的网页模板，包含：
- `name`：模板名称
- `description`：模板描述
- `url_pattern`：URL模式（包含 `{}` 作为主体名称的占位符）
- `category`：分类（government/association/search）
- `InsertContext`：报告中显示的章节标题

### 配置文件（.env）
支持通过环境变量配置程序行为：
```
# 浏览器配置
BROWSER_HEADLESS=True
BROWSER_VIEWPORT=1920x1080
BROWSER_TIMEOUT=30000

# 水印配置
WATERMARK_TEXT=%Y-%m-%d %H:%M:%S
WATERMARK_FONT_SIZE=24
WATERMARK_COLOR=#808080
WATERMARK_OPACITY=0.5

# 输出路径配置
OUTPUT_DIR=output
REPORTS_DIR=output/reports
SCREENSHOTS_DIR=output/screenshots
TEMP_DIR=output/temp
```

## 开发与测试

### 运行测试
```bash
uv run python -m pytest tests/ -v
```

### 项目依赖
```
playwright>=1.40.0       # 浏览器自动化
python-docx>=0.8.11      # Word文档处理
Pillow>=10.0.0           # 图片处理和水印
python-dotenv>=1.0.0     # 环境变量加载
pydantic>=2.0.0          # 数据验证和配置管理
```

## 注意事项

1. **网络连接**：程序需要稳定的网络连接来访问网页
2. **浏览器驱动**：第一次运行前需要安装Playwright浏览器驱动
3. **权限问题**：确保程序有写入输出目录的权限
4. **截图格式**：支持PNG、JPG、JPEG、BMP格式的截图
5. **报告格式**：生成的报告是.docx格式，需要Word或兼容软件打开

## 许可证

本项目采用 MIT 许可证，详情请参见 LICENSE 文件（如果有）。

## 作者信息

项目维护者：Raphael (https://github.com/Raphaellzx)

---

**更新时间**：2026年2月1日
**版本**：0.1.0
