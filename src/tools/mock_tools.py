import json
from typing import List, Dict, Optional
from langchain_core.tools import tool

@tool
def get_customer_details(customer_name: str) -> str:
    """
    根据客户名称查询客户详细信息。
    模拟数据库查询操作。
    """
    print(f"\n[Mock Tool] Searching for customer: {customer_name}")
    # Mock data
    if "ABC" in customer_name:
        return json.dumps({
            "name": "ABC科技",
            "industry": "互联网",
            "city": "上海",
            "employee_count": 120,
            "existing_policy": "None"
        }, ensure_ascii=False)
    else:
        return json.dumps({"error": "Customer not found"}, ensure_ascii=False)

@tool
def recommend_insurance_plans(customer_info: str, budget: int) -> str:
    """
    根据客户信息和预算推荐团险方案。
    返回多个方案选项。
    """
    print(f"\n[Mock Tool] Recommending plans for budget: {budget}")
    # Mock plans
    plans = [
        {
            "id": "PLAN_A",
            "name": "基础版",
            "price": 450,
            "features": ["意外险", "补充医疗"],
            "description": "适合预算有限的基础保障"
        },
        {
            "id": "PLAN_B",
            "name": "标准版",
            "price": 520,
            "features": ["意外险", "补充医疗", "重疾"],
            "description": "性价比最高的全面保障"
        },
        {
            "id": "PLAN_C",
            "name": "尊享版",
            "price": 600,
            "features": ["意外险", "补充医疗", "重疾", "门诊"],
            "description": "包含门诊的高端体验"
        }
    ]
    
    # Simple filtering based on budget (mock logic)
    filtered_plans = [p for p in plans if p["price"] <= budget + 100]
    return json.dumps(filtered_plans, ensure_ascii=False)

@tool
def compare_insurance_plans(plan_ids: List[str]) -> str:
    """
    对比用户选择的指定方案ID。
    返回对比表格数据。
    """
    print(f"\n[Mock Tool] Comparing plans: {plan_ids}")
    
    # Mock comparison data
    all_plans = {
        "PLAN_A": {"price": "450元", "outpatient": "无", "critical_illness": "无"},
        "PLAN_B": {"price": "520元", "outpatient": "无", "critical_illness": "含"},
        "PLAN_C": {"price": "600元", "outpatient": "含", "critical_illness": "含"}
    }
    
    result = {}
    for pid in plan_ids:
        # fuzzy match for demo
        for key in all_plans:
            if pid in key or key in pid:
                 result[key] = all_plans[key]
    
    return json.dumps(result, ensure_ascii=False)

@tool
def generate_quotation(customer_info: str, selected_plan_id: str) -> str:
    """
    生成最终询报价单。
    返回询价单ID和详情。
    """
    print(f"\n[Mock Tool] Generating quote for plan: {selected_plan_id}")
    
    return json.dumps({
        "quote_id": "Q20240501001",
        "status": "Generated",
        "plan_id": selected_plan_id,
        "valid_until": "2024-12-31"
    }, ensure_ascii=False)
