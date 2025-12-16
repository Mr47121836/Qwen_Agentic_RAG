# test_rag_agent.py
import sys
sys.path.append('.')  # 确保可以导入项目模块

from models.agent import RAGAgent
import config

# 测试使用配置文件中的默认模型
print(f"配置文件默认模型: {config.DEFAULT_MODEL}")

# 创建代理
try:
    agent = RAGAgent(model_version=config.DEFAULT_MODEL)
    print("✓ RAGAgent 创建成功")
    
    # 测试简单查询
    response = agent.run("你好，测试一下")
    print(f"✓ 查询成功: {response[:100]}...")
    
except Exception as e:
    print(f"✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()