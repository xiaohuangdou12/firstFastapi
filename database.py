# database.py
import aiomysql
from typing import Optional

# 连接池对象，初始为None
_pool: Optional[aiomysql.Pool] = None

async def init_db_pool():
    """初始化数据库连接池（应用启动时调用）"""
    global _pool
    _pool = await aiomysql.create_pool(
        host='1.116.112.150',       # 数据库主机
        port=3308,              # 端口
        user='root',   # 用户名
        password='123456', # 密码
        db='fastapi_db',     # 数据库名
        minsize=1,              # 连接池最小连接数
        maxsize=10,             # 连接池最大连接数
        autocommit=True,        # 自动提交事务，根据需要设置
        charset='utf8mb4'       # 字符集
    )
    print("数据库连接池已创建")

async def close_db_pool():
    """关闭数据库连接池（应用关闭时调用）"""
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        print("数据库连接池已关闭")

async def get_db_connection():
    """从连接池获取一个数据库连接（依赖项中使用）"""
    if _pool is None:
        raise Exception("数据库连接池未初始化")
    async with _pool.acquire() as conn:
        yield conn


import asyncio


async def test_db_connection():
    try:
        # 初始化数据库连接池
        await init_db_pool()
        print("连接池初始化成功")

        # 获取数据库连接并执行测试查询
        async for conn in get_db_connection():
            async with conn.cursor() as cur:
                # 执行一个简单的查询（例如查询数据库版本）
                await cur.execute("SELECT VERSION()")
                result = await cur.fetchone()
                print(f"数据库版本: {result[0]}")

                # 可以根据需要添加更多测试查询
                # await cur.execute("SELECT 1 + 1")
                # result = await cur.fetchone()
                # print(f"简单计算结果: {result[0]}")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 确保连接池被关闭
        await close_db_pool()
        print("连接池已关闭")


if __name__ == "__main__":
    # 运行测试函数
    asyncio.run(test_db_connection())