from langchain.tools import tool
from pydantic import BaseModel, Field
from simpleeval import simple_eval

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