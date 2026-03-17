import json
from langchain_core.tools import tool

class QuotationSkill:
    """
    Skill set for quotation generation and management.
    """

    name = "quotation_generation"
    description = "生成正式的团险询价单，确认最终方案"
    keywords = ["询价", "报价", "生成", "确认", "单据"]

    @staticmethod
    @tool
    def generate_quotation(customer_info: str, selected_plan_id: str) -> str:
        """
        生成最终询报价单。
        返回询价单ID和详情。
        """
        print(f"\n[QuotationSkill] Generating quote for plan: {selected_plan_id}")
        
        return json.dumps({
            "quote_id": "Q20240501001",
            "status": "Generated",
            "plan_id": selected_plan_id,
            "valid_until": "2024-12-31"
        }, ensure_ascii=False)

    @staticmethod
    def get_tools():
        return [QuotationSkill.generate_quotation]
