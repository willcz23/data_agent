from dotenv import load_dotenv
import os
import pymysql
from pydantic import BaseModel, Field
import simplejson
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from datetime import date
import time
from simpleeval import simple_eval

@tool
def get_date() -> str:
    """
    只有当需要进行有关当前日期的操作调用该函数
    return 当前的日期
    """
    now = date.today()
    return str(now)


class Cal_Schema(BaseModel):
    expression: str = Field(description="要执行的四则运算表达式,用于计算")

@tool(args_schema=Cal_Schema)
def calculator(expression: str) -> str:
    """
    当所有数据查询好，可以用这个计算器计算数值
    不能用来查询数据库
    安全的四则运算计算器，支持 + - * / ( ) 和小数
    """
    try:
        # 清理输入
        expression = expression.strip()
        expression = expression.replace(' ', '')

        # 简单校验：只允许数字、运算符和括号
        if not all(c in '0123456789+-*/().e-' for c in expression):
            return "错误：包含非法字符"

        # 计算结果
        result = simple_eval(expression)
        return f"{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"
    



param_description = """要执行的SQL查询语句"""
class SQL_Query_Schema(BaseModel):
    sql_query: str = Field(description=param_description)

@tool(args_schema=SQL_Query_Schema)
def sql_read(sql_query: str) -> str:
    """
    当需要进行数值计算或数据查询时调用此工具。
    如果有未知的数据，一定必须要使用该工具调用查询。
    该函数在mysql服务器上面运行sql_query代码,完成数据库查询的工作
    使用pymysql连接mysql服务器
    return sql_query查询的结果
    """
    # print("正在使用sql查询")
    load_dotenv()
    host = os.environ["HOST"]
    user = os.environ["USER"]
    mysql_pw = os.environ["MYSQL_PW"]
    db = os.environ["DB"]
    port = os.environ["PORT"]

    connection = pymysql.connect(
        host=host,
        user=user,
        passwd=mysql_pw,
        db=db,
        port=int(port),
        charset='utf8'
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
    finally:
        connection.close()
    
    return simplejson.dumps(results, ensure_ascii=False)

        
class SQL_Extract_Schema(BaseModel):
    sql_query: str = Field(description="用于从数据库中提取数据的SQL语句")
    df_name: str = Field(description="指定用于保存结果的 pandas 变量名称（字符串形式）。")

@tool(args_schema=SQL_Extract_Schema)
def extract_data(sql_query: str, df_name: str) -> str:
    """
    仅在以下情况调用此工具：
    1. 明确需要进行可视化绘图

    禁止用于简单数值计算！
    将MySQL查询结果保存为pandas DataFrame到变量{df_name}
    同时需要注意，编写外部函数的参数消息时,必须是满足json格式的字符串.
    :param sql_query: 字符串形式的SQL查询语句,用于提取MySQL中的某张表。
    :param df_name: 将MySQL数据库中提取的表格进行本地保存时的变量名,以字符串形式表示。
    :return:表格读取和保存结果
    """

    # print("正在调用 extract_data 工具运行 SQL 查询...")

    load_dotenv()
    host = os.environ["HOST"]
    user = os.environ["USER"]
    mysql_pw = os.environ["MYSQL_PW"]
    db = os.environ["DB"]
    port = os.environ["PORT"]

    connection = pymysql.connect(
        host=host,
        user=user,
        passwd=mysql_pw,
        db=db,
        port=int(port),
        charset='utf8'
    )

    try:
        df = pd.read_sql(sql_query, connection)
        globals()[df_name] = df
        print("数据成功提取并保存为全局变量：", df_name)
        return f"成功创建pandas对象 {df_name},包含从 MySQL 提取的数据。"
    except Exception as e:
        return f"执行失败 {e}"
    finally:
        connection.close()


class FigCodeInput(BaseModel):
    py_code: str = Field(
        description="要执行的Python绘图代码。必须使用 matplotlib 或 seaborn 创建图像，并将图像对象（如 fig）赋值给一个变量。"
    )
    fig_var: str = Field(
        default="fig",
        description="图像对象的变量名（在py_code中定义），例如 'fig' 或 'f'。工具将从此变量获取图像对象。"
    )
    file_name: str = Field(
        description="要保存的图片文件名（不含扩展名），例如 'daily_sales_per_sku'。最终文件为 {file_name}.png"
    )


@tool(args_schema=FigCodeInput)
def fig_inter(py_code: str, fig_var: str, file_name: str) -> str:
    """
    执行Python绘图代码，并将图像保存为指定名称的PNG文件。
    如果不需要绘图，就不要调用这个工具
    返回Markdown格式的图片引用，供前端直接显示。
    """

    print(f"🟢 正在执行绘图工具: fig_inter")
    print(f"📌 图像变量名: {fig_var}")
    print(f"📌 期望文件名: {file_name}.png")
    
    current_backend = matplotlib.get_backend()
    matplotlib.use('Agg')
    # print(f"图像保存目录: {images_dir}")
    plt.rcParams['font.sans-serif'] = [
        'SimHei',       # Windows 黑体
        'Microsoft YaHei',  # Windows 微软雅黑
        'PingFang SC',  # MacOS 苹方
        'WenQuanYi Zen Hei',  # Linux
        'Arial Unicode MS'  # 跨平台
    ]
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    local_vars = {"plt": plt, "pd": pd, "sns": sns}
    
    # 添加全局变量到本地环境（重要！）
    local_vars.update(globals())

    try:
        # 设置图像保存路径
        working_dir = os.getcwd()
        base_dir = os.path.join(working_dir, "agent-chat-ui", "public")
        images_dir = os.path.join(base_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
    

        image_filename = f"{file_name}.png"
        abs_path = os.path.join(images_dir, image_filename)
        # 添加时间戳防止浏览器缓存
        cache_buster = int(time.time())
        rel_path = f"/images/{file_name}.png?t={cache_buster}"


        
        print("开始执行绘图代码...")
        exec(py_code, globals(), local_vars)
        
        
        fig = local_vars.get(fig_var)

        print(f"查找变量 {fig_var}: {'找到了' if fig else '未找到'}")
        
        if fig is None:
            # 尝试获取当前图像
            fig = plt.gcf()
            if not fig.axes:
                return "❌ 错误：绘图代码未生成有效图像内容。请检查代码是否正确绘制了图表。"
            print(f"⚠️ 未找到变量 '{fig_var}'，使用 plt.gcf() 获取当前图像。")
        
        if fig:
            fig.savefig(abs_path, bbox_inches='tight', dpi=120, facecolor='w')
            plt.close(fig)  # 立即释放内存
            # fig.savefig(abs_path, bbox_inches='tight')
            
            print(f"✅ 图像已保存: {abs_path}")

            # 返回 Markdown 图片语法（带防缓存参数）
            markdown_image = f"![{file_name}]({rel_path})"
            return markdown_image
        
            # 返回Markdown格式的图片链接，供前端直接显示
            # return f"![Generated Chart]({rel_path})"
        
    except Exception as e:
        import traceback
        error_msg = f"❌ 绘图执行失败: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"绘图失败: {str(e)}"
    
    finally:
        plt.close('all')
        matplotlib.use(current_backend)



prompt = """
你是一名经验丰富的智能数据分析助手，专注于电商运营数据分析（尤其Mercado平台）。你的核心任务是帮助用户高效执行数据库操作、数据提取、可视化及关键业务指标计算。
**核心原则：**
1.  **专业严谨：** 所有计算必须严格遵循下方定义的**「业务指标计算规范」**，涉及到计算必须根据计算规范来设计sql语句统计。
2.  **高效精准：** 优先使用指定工具，输出结果需精确无误，不可以编造数据。
3.  **清晰沟通：** 使用中文，回答简洁。如需信息，主动提出明确问题。
4.  **数据驱动：** **基于数据事实输出，禁止编造工具、数据或逻辑**。
---
**工具规范：**
1.  **`sql_read` (数据库查询):**
    *   当用户需要**获取数据**或**执行查询**或**数值计算**时调用。
    *   根据用户需求生成**精确SQL语句**。参数已预置。
    *   *示例：`SELECT sku, units FROM T_mercado_sales_record
2.  **`extract_data` (数据表提取):**
    *   仅在以下情况调用此工具：**明确需要进行可视化绘图**
    *   禁止用于简单数值计算！
3.  **`fig_inter` (绘图代码执行):**
    *   只有当用户主动要求**可视化**时调用。
    *   **前提：** 相关数据必须已通过 `extract_data` 加载为DataFrame。
    *   生成**完整绘图代码**：
        *   必须创建**`fig`图像对象** (如 `fig = plt.figure()` 或 `fig, ax = plt.subplots()`)。
        *   禁止调用 `plt.show()`，否则无法保存图片。
        *   在代码末尾**明确保存图片** (如 `fig.savefig('images/sales_trend.png')`)。
    *   回答中**必须用Markdown插入图片**: `![描述](images/sales_trend.png)`

---

**业务指标计算规范 (MUST FOLLOW - 使用前务必确保必要数据已加载！)：**
以下是核心业务指标的定义、计算公式、所需数据字段及关键判断逻辑。**你必须严格按照此逻辑进行计算，并清晰说明数据来源和假设。**

*   **`SKU`** = `T_mercado_sales_record.sku`
*   **`ASIN/ID`** = `T_mercado_sales_record.publication_id`
*   **`总销量(件)`** = `SUM(T_mercado_sales_record.units)` (特定条件下)
*   **`日均销量(件)`** = `总销量 / 30` (默认按30天计算)
*   **`退货总计(件)`** = `SUM(CASE WHEN T_mercado_sales_record.cancellations_refunds < 0 THEN ABS(T_mercado_sales_record.cancellations_refunds) ELSE 0 END)` [`cancellations_refunds < 0 表示退货`]
*   **`净销量(件)`** = `总销量 - 退货总计`
*   **`净销售额(RMB)`** = `SUM(CASE WHEN T_mercado_sales_record.total_amount > 0 THEN (T_mercado_sales_record.product_revenue + COALESCE(T_mercado_sales_record.cancellations_refunds, 0)) ELSE 0 END)` [`total_amount > 0 为有效订单`]
*   **`采购单价(RMB)`** = `T_mercado_product_cost.purchase_price_rmb` (通过`SKU`关联)
*   **`运费单价(RMB)`** = `T_mercado_product_cost.shipping_unit_price_rmb` (通过`SKU`关联)
*   **`售后损耗(RMB)`** = `退货总计 * (采购单价 + 运费单价 + 0.8)` [`0.8 RMB 是预估单件退货损耗`]
*   **`售后损耗率`** = `售后损耗 / 净销售额` (分母为RMB值)
*   **`回款净所得(RMB)`** = `SUM(CASE WHEN T_mercado_sales_record.total_amount > 0 THEN T_mercado_sales_record.total_amount * 0.99 ELSE 0 END)` [`有效订单总额乘以汇损系数0.99`]。   (需先加载`T_mercado_product_cost`按SKU关联)
*   **`总采购成本(RMB)`** = `采购单价 * 净销量` (需先加载`T_mercado_product_cost`按SKU关联)
*   **`总运费成本(RMB)`** = `运费单价 * 净销量` (需先加载`T_mercado_product_cost`按SKU关联)
*   **`打包费(RMB)`** = `净销量 * 0.8` [`0.8 RMB 是单件打包费`]
*   **`毛利润(RMB)`** = `回款净所得 - 总采购成本 - 总运费成本 - 打包费 - 售后损耗`
*   **`毛利率`** = `毛利润 / 净销售额`
*   **`广告费用(RMB)`** = `SUM(T_mercado_fee_advertisement.investment)` (通过`publication_id` (`ASIN/ID`)关联)
*   **`广告费用占比`** = `广告费用 / 净销售额`
*   **`测评费用(RMB)`** = `SUM(T_mercado_product_cost.evaluation_fee_rmb)` (按`SKU`统计)
*   **`测评费用占比`** = `测评费用 / 净销售额`
*   **`仓储费(RMB)`** (按SKU均摊):
    *   总仓储费 = `SUM(CASE WHEN T_mercado_fee_summary.charge_detail IN ('Cargo por servicio de almacenamiento Full', 'Cargo por stock antiguo en Full', 'Cargo por retiro de stock Full') THEN T_mercado_fee_summary.charge_amount ELSE 0 END)`
    *   总在库数量(`SKU`粒度) = `SUM(T_mercado_inventory.sellable_units)` (在计算周期内)
    *   单个SKU均摊仓储费 = `总仓储费 * (该SKU在库数量 / 总在库数量)`
*   **`仓储费占比`** = `仓储费 / 净销售额`
*   **`纯利润(RMB)`** = `毛利润 - 广告费用 - 测评费用 - 仓储费`
*   **`纯利率`** = `纯利润 / 净销售额`

**指标计算关键点：**
    **数据完整性：** 计算某指标前，必须确保相关数据表(如果没有自主访问数据库加载关联)已通过`extract_data`正确加载并关联。
    **用户要求计算指标时，你必须输出指标的计算公式，以确保正确**
---

**回答与输出要求：**
1.  **明确执行步骤：** 清晰说明将使用哪个工具及原因。
2.  **展示关键结果：** 工具返回JSON数据后，**简要说明**并展示**核心结果摘要**（如查询行数、关键指标值、绘图主题）。
3.  **绘图必备：** 生成图片必须按规范保存并**插入Markdown显示**。禁止只输出文件路径文字。
4.  **质疑与澄清：** 若用户请求违反计算规范、工具限制或数据缺失，生成sql查找。
5.  **重点突出：** 对关键业务指标结果（如纯利率、毛利率）做适当强调。
6.  **最后输出答案的时候，不需要关键说明等等多余信息，只要返回简洁的结果就行了**

**如果没有数据，自行调用工具去数据库查找**
**请严格遵守以上规则，为用户提供精准、可靠、符合业务逻辑的数据分析支持。**
"""

tools = [calculator, sql_read, extract_data, fig_inter, get_date]

load_dotenv()

model = ChatOpenAI(
    model="qwen3-235b-a22b-instruct-2507",
    api_key=os.environ["QWEN_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

graph = create_react_agent(model=model, tools=tools, prompt=prompt)


