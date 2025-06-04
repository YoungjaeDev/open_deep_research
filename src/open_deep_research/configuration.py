import os
from enum import Enum
from dataclasses import dataclass, fields
from typing import Any, Optional, Dict 

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

DEFAULT_REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list or table) that distills the main body sections 
   - Provide a concise summary of the report"""

DEFAULT_REPORT_STRUCTURE_KO = """다음 구조를 사용하여 사용자가 제공한 주제에 대한 보고서를 작성하세요:

1. 서론 (연구 불필요)
   - 주제 영역에 대한 간략한 개요

2. 본문 섹션들:
   - 각 섹션은 사용자가 제공한 주제의 하위 주제에 초점을 맞춰야 함
   
3. 결론
   - 본문 섹션들을 요약한 1개의 구조적 요소(목록 또는 표)를 목표로 함
   - 보고서의 간결한 요약 제공"""


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    EXA = "exa"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    LINKUP = "linkup"
    DUCKDUCKGO = "duckduckgo"
    GOOGLESEARCH = "googlesearch"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    # Common configuration
    report_structure: str = DEFAULT_REPORT_STRUCTURE # Defaults to the default report structure
    search_api: SearchAPI = SearchAPI.TAVILY # Default to TAVILY
    search_api_config: Optional[Dict[str, Any]] = None
    
    # Graph-specific configuration
    number_of_queries: int = 2 # Number of search queries to generate per iteration
    max_search_depth: int = 2 # Maximum number of reflection + search iterations
    # planner_provider: str = "anthropic"  # Defaults to Anthropic as provider
    planner_provider: str = "openai" # Changed to OpenAI as provider
    planner_model: str = "o4-mini" # Changed to OpenAI o4-mini
    planner_model_kwargs: Optional[Dict[str, Any]] = None # kwargs for planner_model
    writer_provider: str = "openai" # Changed to OpenAI as provider
    writer_model: str = "gpt-4.1" # Changed to OpenAI gpt-4.1
    writer_model_kwargs: Optional[Dict[str, Any]] = None # kwargs for writer_model
    
    # Multi-agent specific configuration
    supervisor_model: str = "openai:gpt-4.1" # Model for supervisor agent in multi-agent setup
    researcher_model: str = "openai:gpt-4.1" # Model for research agents in multi-agent setup 

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
