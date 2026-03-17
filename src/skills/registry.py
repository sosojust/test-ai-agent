from typing import List, Type
from langchain_core.tools import BaseTool
from src.skills.customer import CustomerSkill
from src.skills.insurance import InsuranceSkill
from src.skills.quotation import QuotationSkill

class SkillRegistry:
    """
    Registry for managing and retrieving skills.
    """
    
    _skills = [
        CustomerSkill,
        InsuranceSkill,
        QuotationSkill
    ]
    
    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """Get all tools from all skills."""
        tools = []
        for skill in cls._skills:
            tools.extend(skill.get_tools())
        return tools

    @classmethod
    def retrieve_skills(cls, query: str) -> List[BaseTool]:
        """
        Retrieve relevant tools based on query.
        Simple keyword matching for Demo.
        """
        if not query:
            return cls.get_all_tools()
            
        relevant_tools = []
        query_lower = query.lower()
        
        print(f"\n[SkillRegistry] Retrieving skills for query: '{query}'")
        
        for skill in cls._skills:
            # Check if any keyword matches
            is_relevant = False
            
            # Check description
            if skill.description and any(k in skill.description for k in query_lower.split()):
                is_relevant = True
                
            # Check keywords
            if hasattr(skill, 'keywords'):
                for kw in skill.keywords:
                    if kw in query_lower:
                        is_relevant = True
                        break
            
            if is_relevant:
                print(f"  -> Matched Skill: {skill.name}")
                relevant_tools.extend(skill.get_tools())
                
        # Fallback: if no skills matched but query exists, return all (or handle as needed)
        # For demo, if no match, maybe we return empty list? 
        # But Agent might need to chat.
        # Let's return all if no match found to be safe for now, 
        # or better: return empty list so Agent just chats if no tool is relevant.
        if not relevant_tools:
            print("  -> No specific skill matched. Returning empty tool list.")
            return []
            
        return relevant_tools
