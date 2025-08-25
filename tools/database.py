from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.tools import tool
import os
import pymysql
import simplejson
import pandas as pd

load_dotenv()

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
    except Exception as e:
        return f"wrong: {e}"
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