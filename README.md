# Data Agent

一个基于 LangGraph 和 LangChain 的智能数据代理系统，支持自然语言交互式数据分析。前后端分离架构，搭配现代化 UI 实现流畅的对话式数据处理体验。

## 安装

### 1. 克隆项目仓库

```shell
git clone git@github.com:willcz23/data_agent.git
cd data_agent
```

### 2. 创建并激活虚拟环境（使用 Conda）

```shell
conda create -n data_agent 
conda activate data_agent
```

### 3. 安装 Python 依赖

```shell
pip install -r requirements.txt
```

## 🚀 运行项目

本项目由 **前端（Agent Chat UI）** 和 **后端（LangGraph 服务）** 两部分组成。

### 1. 启动前端

项目使用 [langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) 作为交互界面。

```shell
git clone https://github.com/langchain-ai/agent-chat-ui.git
cd agent-chat-ui
```

安装依赖（需提前安装 [pnpm](https://pnpm.io/zh/installation)）：

```shell
pnpm install
```

启动开发服务器：

```shell
pnpm dev
```

📌 前端默认运行在 `http://localhost:3000`

---

### 2. 启动后端

回到 `data_agent` 项目根目录，启动 LangGraph 服务：

```shell
langgraph dev
```


## 配置说明

创建 `.env` 文件并填写以下内容：

```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=data_agent_demo
DATABASE_URL=sqlite:///./test.db  # 或其他数据库
```

现在你可以访问 `http://localhost:3000` 开始与你的数据对话！
