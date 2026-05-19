#!/usr/bin/env python3
"""
第1周Day 1：第一个AI智能体程序
学习目标：
1. Python基础语法
2. 函数定义和调用
3. 简单的智能体逻辑
"""

# 1. 变量和数据类型
agent_name = "学习助手"
version = 1.0
is_active = True

print(f"=== {agent_name} v{version} ===")
print(f"状态: {'在线' if is_active else '离线'}")

# 2. 列表和字典
capabilities = ["回答问题", "提供建议", "学习新知识"]
knowledge_base = {
    "python": "Python是一种高级编程语言",
    "ai_agent": "AI智能体是能够感知环境并采取行动的程序"
}

print(f"\n能力列表: {capabilities}")
print(f"知识库包含: {list(knowledge_base.keys())}")

# 3. 函数定义
def greet_user(name):
    """问候用户"""
    return f"你好，{name}！我是{agent_name}，很高兴为你服务。"

def answer_question(question):
    """回答问题"""
    if question in knowledge_base:
        return knowledge_base[question]
    else:
        return "这个问题我还在学习中，让我查查资料..."

def learn_new_knowledge(topic, description):
    """学习新知识"""
    knowledge_base[topic] = description
    return f"已学习关于'{topic}'的知识！"

# 4. 主程序逻辑
def main():
    print("\n" + "="*40)
    print("智能体演示开始")
    print("="*40)
    
    # 测试函数
    print(greet_user("AI学习者"))
    
    # 回答问题
    questions = ["python", "ai_agent", "machine_learning"]
    for q in questions:
        print(f"\n问题: '{q}'是什么？")
        print(f"回答: {answer_question(q)}")
    
    # 学习新知识
    print(f"\n{learn_new_knowledge('git', 'Git是分布式版本控制系统')}")
    print(f"现在知识库包含: {list(knowledge_base.keys())}")
    
    print("\n" + "="*40)
    print("演示结束！继续学习吧！")
    print("="*40)

# 5. 条件判断
if __name__ == "__main__":
    main()
    
    # 额外练习：循环
    print("\n📚 今日学习目标:")
    goals = ["安装Python环境", "学习基础语法", "编写第一个程序", "理解智能体概念"]
    for i, goal in enumerate(goals, 1):
        print(f"{i}. {goal}")