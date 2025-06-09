import json
from app.utils.common_utils import transform_link
from openai import OpenAI
from app.utils.log_util import logger
import time
from app.schemas.response import AgentMessage, CoderMessage, WriterMessage
from app.utils.enums import AgentType
from app.utils.redis_manager import redis_manager
import re
from litellm import acompletion


class LLM:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        task_id: str,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.chat_count = 0
        self.max_tokens: int | None = None  # 添加最大token数限制
        self.task_id = task_id

    async def chat(
        self,
        history: list = None,
        tools: list = None,
        tool_choice: str = None,
        max_retries: int = 8,  # 添加最大重试次数
        retry_delay: float = 1.0,  # 添加重试延迟
        top_p: float | None = None,  # 添加top_p参数,
        agent_name: str = "NO_NAME",  # CoderAgent or WriterAgent
        sub_title: str | None = None,
    ) -> str:
        logger.info(f"subtitle是:{sub_title}")

        kwargs = {
            "api_key": self.api_key,
            "model": self.model,
            "messages": history,
            "stream": False,
            "top_p": top_p,
        }

        if tools:
            # 根据模型类型自动转换工具格式
            kwargs["tools"] = self._convert_tools_for_model(tools)

            # Gemini 使用 tool_choice="auto" 会自动转成 {"mode":"AUTO"}
            # OpenAI 依旧保持 "auto"
            kwargs["tool_choice"] = tool_choice

        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens

        if self.base_url:
            kwargs["base_url"] = self.base_url

        # TODO: stream 输出
        for attempt in range(max_retries):
            try:
                # completion = self.client.chat.completions.create(**kwargs)
                response = await acompletion(**kwargs)
                logger.info(f"API返回: {response}")
                if not response or not hasattr(response, "choices"):
                    raise ValueError("无效的API响应")
                self.chat_count += 1
                await self.analyse_completion(response, agent_name, sub_title)
                return response
            except json.JSONDecodeError:
                logger.error(f"第{attempt + 1}次重试: API返回无效JSON")
                if attempt < max_retries - 1:  # 如果不是最后一次尝试
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                logger.debug(f"请求参数: {kwargs}")
                raise  # 如果所有重试都失败，则抛出异常

    async def analyse_completion(self, completion, agent_name, sub_title):
        logger.info(f"subtitle是:{sub_title}")

        code = ""
        if (
            hasattr(completion.choices[0].message, "tool_calls")
            and completion.choices[0].message.tool_calls
        ):
            tool_call = completion.choices[0].message.tool_calls[0]
            if tool_call.function.name == "execute_code":
                code = json.loads(tool_call.function.arguments)["code"]
        (
            await self.send_message(
                agent_name, completion.choices[0].message.content, code, sub_title
            )
        )

    async def send_message(self, agent_name, content, code="", sub_title=None):
        logger.info(f"subtitle是:{sub_title}")
        if agent_name == "CoderAgent":
            agent_msg: CoderMessage = CoderMessage(content=content, code=code)
        elif agent_name == "WriterAgent":
            # 处理 Markdown 格式的图片语法
            content = transform_link(self.task_id, content)
            agent_msg: WriterMessage = WriterMessage(
                content=content, sub_title=sub_title
            )
        else:
            raise ValueError(f"无效的agent_name: {agent_name}")

        await redis_manager.publish_message(
            self.task_id,
            agent_msg,
        )

    def _convert_tools_for_model(self, tools: list):
        """根据所选模型自动转换工具 schema。

        - OpenAI / DeepSeek / Anthropic: 继续使用 {"type":"function","function":{...}}
        - Google Gemini v1beta: 需要包装成 {"functionDeclarations": [...]} 结构。
        """
        # 仅当目标模型包含 "gemini" 关键字并且当前 tools 是 openai-style 时转换
        model_lower = self.model.lower()
        is_gemini = "gemini" in model_lower

        # 判断第一个元素是否已经是 functionDeclarations 格式
        if not tools or not is_gemini:
            return tools

        if "functionDeclarations" in tools[0]:
            # 已经是 gemini 风格
            return tools

        # 否则执行转换
        converted = []
        for t in tools:
            if "function" in t:
                converted.append({"functionDeclarations": [t["function"]]})
            else:
                converted.append(t)
        return converted


# class DeepSeekModel(LLM):
#     def __init__(
#         self,
#         api_key: str,
#         model: str,
#         base_url: str,
#         task_id: str,
#     ):
#         super().__init__(api_key, model, base_url, task_id)
# self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)


async def simple_chat(model: LLM, history: list) -> str:
    """
    Description of the function.

    Args:
        model (LLM): 模型
        history (list): 构造好的历史记录（包含system_prompt,user_prompt）

    Returns:
        return_type: Description of the return value.
    """
    kwargs = {
        "api_key": model.api_key,
        "model": model.model,
        "messages": history,
        "stream": False,
    }

    if model.base_url:
        kwargs["base_url"] = model.base_url

    response = await acompletion(**kwargs)

    return response.choices[0].message.content
