from typing import List, Dict, Any
from semanticscholar import SemanticScholar, PaginatedResults

# Gemini 2.5（Generative AI v1beta）函数调用要求的格式
# 参考官方文档：https://developers.generativeai.google/api/rest/v1beta/HarmCategory
# 需要使用 tools => [{"functionDeclarations": [ ... ]}] 的结构，而不是 OpenAI 的
# {"type": "function", "function": {...}} 结构。

# OpenAI Chat Completions 风格的工具定义（默认使用）
tools_openai = [
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": (
                "Execute Python code in an isolated Jupyter kernel and return the textual stdout/stderr. "
                "If the executed code produces a plot or any image, save it to the working directory and "
                "return the literal string '[image]' so the user knows an image was generated. "
                "The kernel persists between calls, keeping variables in memory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Valid Python source code to execute."
                    }
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        },
    }
]

# Gemini Generative AI v1beta 风格的工具声明
tools_gemini = [
    {
        "functionDeclarations": [
            {
                "name": "execute_code",
                "description": (
                    "Execute Python code in an isolated Jupyter kernel and return the textual stdout/stderr. "
                    "If the executed code produces a plot or any image, save it to the working directory and "
                    "return the literal string '[image]'. "
                    "The kernel persists between calls, keeping variables in memory."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Valid Python source code to execute."
                        }
                    },
                    "required": ["code"],
                    "additionalProperties": False,
                },
            }
        ]
    }
]

# 默认暴露 openai 风格，代码内部会根据目标模型转换
tools = tools_openai

# have installed: numpy scipy pandas matplotlib seaborn scikit-learn xgboost

# TODO: pip install python

# TODO: read files

# TODO: get_cites


def search_papers(query: str) -> List[Dict[str, Any]]:
    """Search for papers using a query string."""
    sch = SemanticScholar()
    results: PaginatedResults = sch.search_paper(query, limit=10)
    return [
        {
            "title": paper.title,
            "abstract": paper.abstract,
            "authorsName": [author.name for author in paper.authors],
            "citations": [citation.title for citation in paper.citations],
        }
        for paper in results
    ]


## writeragent tools
