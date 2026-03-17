import json
from langchain_core.tools import tool

class CustomerSkill:
    """
    Skill set for customer information management.
    """
    
    name = "customer_info"
    description = "查询客户详细信息，包括企业名称、人员规模、行业、已有保单等"
    keywords = ["客户", "公司", "企业", "人数", "规模", "行业", "查询"]
    
    @staticmethod
    @tool
    def get_customer_details(customer_name: str) -> str:
        """
        根据客户名称查询客户详细信息。
        模拟数据库查询操作。
        """
        print(f"\n[CustomerSkill] Searching for customer: {customer_name}")
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

    @staticmethod
    def get_tools():
        return [CustomerSkill.get_customer_details]
