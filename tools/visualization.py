from pydantic import BaseModel, Field
from langchain.tools import tool
import matplotlib
import matplotlib.pyplot as plt
import os
import time
import seaborn as sns
import pandas as pd

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
    执行Python绘图代码
    如果不需要绘图，就不要调用这个工具
    返回Markdown格式的图片引用，供前端直接显示。
    """

    print(f"正在执行绘图工具: fig_inter")
    print(f"图像变量名: {fig_var}")
    print(f"期望文件名: {file_name}.png")
    
    current_backend = matplotlib.get_backend()
    matplotlib.use('Agg')
    plt.rcParams['font.sans-serif'] = [
        'SimHei',       # Windows 黑体
        'Microsoft YaHei',  # Windows 微软雅黑
        'PingFang SC',  # MacOS 苹方
        'WenQuanYi Zen Hei',  # Linux
        'Arial Unicode MS'  # 跨平台
    ]
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


    local_vars = {"plt": plt, "pd": pd, "sns": sns, "os": os}
    
    # 添加全局变量到本地环境（重要！）
    local_vars.update(globals())
    
    # 导入 database 模块以访问其中设置的全局变量
    try:
        import tools.database as db_module
        local_vars.update(db_module.__dict__)
        print(f"已导入tools.database数据")
    except Exception as e:
        print(f"⚠️ 无法加载 database 模块的全局变量: {e}")

    try:
        # 设置图像保存路径
        current_dir = os.path.dirname(__file__)  # tools/ 目录
        project_root = os.path.dirname(current_dir)  # 项目根目录
        # 3. 定位前端 public 目录
        frontend_public = os.path.join(project_root, "agent-chat-ui", "public")
        frontend_public = os.path.abspath(frontend_public)  # 转为绝对路径
        # 4. 图片保存目录
        images_dir = os.path.join(frontend_public, "images")
        os.makedirs(images_dir, exist_ok=True)

        abs_path = os.path.join(images_dir, f"{file_name}.png")
        cache_buster = int(time.time())
        rel_path = f"/images/{file_name}.png?t={cache_buster}"  # 前端通过此 URL 访问

        print(f"🖼️  图像将保存到: {abs_path}")
        print(f"🌐 前端访问路径: {rel_path}")
        print("开始执行绘图代码...")
        
        exec(py_code, globals(), local_vars)
        fig = local_vars.get(fig_var)

        if fig is None:
            fig = plt.gcf()
            if not fig.axes:
                return "❌ 错误：绘图代码未生成有效图像内容。请检查代码是否正确绘制了图表。"
            print(f"⚠️ 未找到变量 '{fig_var}'，使用 plt.gcf() 获取当前图像。")

        fig.savefig(abs_path, bbox_inches='tight', dpi=120, facecolor='w')
        plt.close(fig)
        print(f"✅ 图像已保存: {abs_path}")
        
        return f"![{file_name}]({rel_path})"
        
    except Exception as e:
        import traceback
        error_msg = f"❌ 绘图执行失败: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"绘图失败: {str(e)}, {error_msg}"
    
    finally:
        plt.close('all')
        matplotlib.use(current_backend)
