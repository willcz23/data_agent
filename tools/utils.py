from langchain.tools import tool
from datetime import date

@tool
def get_date() -> str:
    """
    只有当需要进行有关当前日期的操作调用该函数
    return 当前的日期
    """
    now = date.today()
    return str(now)