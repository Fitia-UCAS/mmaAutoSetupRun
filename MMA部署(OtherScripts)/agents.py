import json
from app.core.llm import LLM
from app.core.prompts import (
    get_completion_check_prompt,
    get_reflection_prompt,
    get_writer_prompt,
    CODER_PROMPT,
    MODELER_PROMPT,
)
from app.core.functions import tools
from app.models.model import CoderToWriter
from app.models.user_output import UserOutput
from app.utils.enums import CompTemplate, FormatOutPut
from app.utils.log_util import logger
from app.config.setting import settings
from app.utils.common_utils import get_current_files
from app.utils.redis_manager import redis_manager
from app.schemas.response import SystemMessage
from app.tools.base_interpreter import BaseCodeInterpreter


class Agent:
    def __init__(
        self,
        task_id: str,
        model: LLM,
        max_chat_turns: int = 30,  # 单个agent最大对话轮次
        user_output: UserOutput = None,
        max_memory: int = 20,  # 最大记忆轮次
    ) -> None:
        self.task_id = task_id
        self.model = model
        self.chat_history: list[dict] = []  # 存储对话历史
        self.max_chat_turns = max_chat_turns  # 最大对话轮次
        self.current_chat_turns = 0  # 当前对话轮次计数器
        self.user_output = user_output
        self.max_memory = max_memory  # 最大记忆轮次

    async def run(self, prompt: str, system_prompt: str, sub_title: str) -> str:
        """
        执行agent的对话并返回结果和总结

        Args:
            prompt: 输入的提示

        Returns:
            str: 模型的响应
        """
        try:
            logger.info(f"{self.__class__.__name__}:开始:执行对话")
            self.current_chat_turns = 0  # 重置对话轮次计数器

            # 更新对话历史
            self.append_chat_history({"role": "system", "content": system_prompt})
            self.append_chat_history({"role": "user", "content": prompt})

            # 获取历史消息用于本次对话
            response = await self.model.chat(
                history=self.chat_history,
                agent_name=self.__class__.__name__,
                sub_title=sub_title,
            )
            response_content = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": response_content})
            logger.info(f"{self.__class__.__name__}:完成:执行对话")
            return response_content
        except Exception as e:
            error_msg = f"执行过程中遇到错误: {str(e)}"
            logger.error(f"Agent执行失败: {str(e)}")
            return error_msg

    def append_chat_history(self, msg: dict) -> None:
        self.clear_memory()
        self.chat_history.append(msg)
        # self.user_output.data_recorder.append_chat_history(
        # msg, agent_name=self.__class__.__name__
        # )

    def clear_memory(self):
        logger.info(f"{self.__class__.__name__}:清除记忆")
        if len(self.chat_history) <= self.max_memory:
            return

        # 使用切片保留第一条和最后两条消息
        self.chat_history = self.chat_history[:2] + self.chat_history[-5:]


class ModelerAgent(Agent):  # 继承自Agent类而不是BaseModel
    def __init__(
        self,
        model: LLM,
        max_chat_turns: int = 30,  # 添加最大对话轮次限制
    ) -> None:
        super().__init__(model, max_chat_turns)
        self.system_prompt = MODELER_PROMPT


# 代码强
class CoderAgent(Agent):  # 同样继承自Agent类
    def __init__(
        self,
        task_id: str,
        model: LLM,
        work_dir: str,  # 工作目录
        max_chat_turns: int = settings.MAX_CHAT_TURNS,  # 最大聊天次数
        max_retries: int = settings.MAX_RETRIES,  # 最大反思次数
        code_interpreter: BaseCodeInterpreter = None,
    ) -> None:
        super().__init__(task_id, model, max_chat_turns)
        self.work_dir = work_dir
        self.max_retries = max_retries
        self.is_first_run = True
        self.system_prompt = CODER_PROMPT
        self.code_interpreter = code_interpreter

    async def run(self, prompt: str, subtask_title: str) -> CoderToWriter:
        logger.info(f"{self.__class__.__name__}:开始:执行子任务: {subtask_title}")
        self.code_interpreter.add_section(subtask_title)

        # 如果是第一次运行，则添加系统提示
        if self.is_first_run:
            logger.info("首次运行，添加系统提示和数据集文件信息")
            self.is_first_run = False
            self.append_chat_history({"role": "system", "content": self.system_prompt})
            # 当前数据集文件
            self.append_chat_history(
                {
                    "role": "user",
                    "content": f"当前文件夹下的数据集文件{get_current_files(self.work_dir, 'data')}",
                }
            )

        # 添加 sub_task
        logger.info(f"添加子任务提示: {prompt}")
        self.append_chat_history({"role": "user", "content": prompt})

        retry_count = 0
        last_error_message = ""
        task_completed = False

        if self.current_chat_turns >= self.max_chat_turns:
            logger.error(f"超过最大聊天次数: {self.max_chat_turns}")
            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content="超过最大聊天次数", type="error"),
            )
            raise Exception(
                f"Reached maximum number of chat turns ({self.max_chat_turns}). Task incomplete."
            )

        if retry_count >= self.max_retries:
            logger.error(f"超过最大尝试次数: {self.max_retries}")
            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content="超过最大尝试次数", type="error"),
            )
            raise Exception(
                f"Failed to complete task after {self.max_retries} attempts. Last error: {last_error_message}"
            )

        # try:
        while (
            not task_completed
            and retry_count < self.max_retries
            and self.current_chat_turns < self.max_chat_turns
        ):
            self.current_chat_turns += 1
            logger.info(f"当前对话轮次: {self.current_chat_turns}")
            response = await self.model.chat(
                history=self.chat_history,
                tools=tools,
                tool_choice="auto",
                agent_name=self.__class__.__name__,
            )

            # 如果有工具调用
            if (
                hasattr(response.choices[0].message, "tool_calls")
                and response.choices[0].message.tool_calls
            ):
                logger.info("检测到工具调用")
                # 获取模型返回的所有工具调用
                tool_calls = response.choices[0].message.tool_calls
                full_content = response.choices[0].message.content

                # 更新对话历史 - 添加助手的响应，包含所有工具调用
                # 确保 tool_calls 列表中的每个元素都是符合预期的字典结构
                assistant_tool_calls_history = []
                for tc in tool_calls:
                    assistant_tool_calls_history.append(
                        {
                            "id": tc.id,
                            "type": tc.type,  # 使用来自工具调用对象的实际类型
                            "function": {
                                "name": tc.function.name,
                                "arguments": str(tc.function.arguments), # 显式确保参数是字符串
                            },
                        }
                    )

                self.append_chat_history(
                    {
                        "role": "assistant",
                        "content": None,  # 当存在 tool_calls 时，显式将 content 设置为 None
                        "tool_calls": assistant_tool_calls_history,
                    }
                )

                all_tool_outputs_for_completion_check = []

                for tool_call in tool_calls:
                    tool_id = tool_call.id
                    tool_function_name = tool_call.function.name
                    tool_arguments_str = tool_call.function.arguments

                    if tool_function_name == "execute_code":
                        logger.info(f"调用工具: {tool_function_name}")
                        await redis_manager.publish_message(
                            self.task_id,
                            SystemMessage(
                                content=f"代码手调用{tool_function_name}工具"
                            ),
                        )
                        try:
                            # 确保 arguments 是有效的 JSON 字符串
                            tool_arguments = json.loads(tool_arguments_str)
                            code = tool_arguments.get("code", "") # 安全获取 code
                        except json.JSONDecodeError as e:
                            logger.error(f"工具参数JSON解析错误: {e}，原始参数: {tool_arguments_str}")
                            # 如果参数解析失败，记录错误并跳过此工具调用或返回错误信息
                            error_message_for_llm = f"Error: Invalid arguments for tool {tool_function_name}. JSONDecodeError: {e}. Arguments: {tool_arguments_str}"
                            self.append_chat_history(
                                {
                                    "role": "tool",
                                    "content": json.dumps({"error": error_message_for_llm}),
                                    "tool_call_id": tool_id,
                                    "name": tool_function_name
                                }
                            )
                            # 可以选择继续处理下一个工具调用，或者标记错误并重试
                            # 这里我们选择记录错误并继续，让LLM决定如何处理
                            last_error_message = error_message_for_llm
                            all_tool_outputs_for_completion_check.append(error_message_for_llm)
                            continue # 跳过当前工具调用

                        # 执行工具调用
                        logger.info(f"执行工具调用: {tool_function_name} with code:\n{code}")
                        (
                            text_to_gpt,
                            error_occurred,
                            error_message,
                        ) = await self.code_interpreter.execute_code(code)

                        # 添加工具执行结果
                        if error_occurred:
                            self.append_chat_history(
                                {
                                    "role": "tool",
                                    "content": json.dumps({"error": error_message}),
                                    "tool_call_id": tool_id,
                                    "name": tool_function_name
                                }
                            )
                            logger.warning(f"代码执行错误: {error_message}")
                            retry_count += 1
                            logger.info(f"当前尝试次:{retry_count} / {self.max_retries}")
                            last_error_message = error_message
                            all_tool_outputs_for_completion_check.append(error_message)

                            # 如果一个工具调用失败，我们可能需要决定是否继续执行其他工具调用
                            # 或者立即进入反思阶段。当前逻辑是继续执行所有工具调用，然后统一反思。
                            # 如果需要立即反思，可以在这里添加逻辑并跳出循环
                        else:
                            self.append_chat_history(
                                {
                                    "role": "tool",
                                    "content": json.dumps({"output": text_to_gpt}),
                                    "tool_call_id": tool_id,
                                    "name": tool_function_name
                                }
                            )
                            all_tool_outputs_for_completion_check.append(text_to_gpt)
                    else:
                        logger.warning(f"未知的工具名称: {tool_function_name}")
                        # 对于未知工具，也需要添加一个 tool 响应
                        unknown_tool_message = f"Error: Unknown tool name '{tool_function_name}' encountered."
                        self.append_chat_history(
                            {
                                "role": "tool",
                                "content": json.dumps({"error": unknown_tool_message}),
                                "tool_call_id": tool_id,
                                "name": tool_function_name
                            }
                        )
                        all_tool_outputs_for_completion_check.append(unknown_tool_message)

                # 所有工具调用执行完毕后，检查是否有错误发生，并决定是否进入反思
                if any(err in str(out) for err in ["Error:", "error:", "Traceback"] for out in all_tool_outputs_for_completion_check) or retry_count > 0:
                    # 汇总所有工具的输出/错误信息用于反思
                    combined_tool_outputs = "\n".join(all_tool_outputs_for_completion_check)
                    reflection_prompt = get_reflection_prompt(combined_tool_outputs, "Multiple tool calls attempted.") # 第二个参数可以更具体
                    await redis_manager.publish_message(
                        self.task_id,
                        SystemMessage(content="代码手反思纠正错误(多工具调用)", type="error"),
                    )
                    self.append_chat_history(
                        {"role": "user", "content": reflection_prompt}
                    )
                    continue # 返回循环顶部，让模型基于反思生成新的响应

                # 如果所有工具都成功执行
                # 检查任务完成情况时也计入对话轮次
                self.current_chat_turns += 1
                logger.info(
                    f"当前对话轮次: {self.current_chat_turns} / {self.max_chat_turns}"
                )
                # 使用所有执行结果生成检查提示
                logger.info("判断是否完成(多工具调用)")

                # 将所有工具的成功输出合并，用于完成检查
                successful_outputs = "\n".join(all_tool_outputs_for_completion_check)
                completion_check_prompt = get_completion_check_prompt(
                    prompt, successful_outputs
                )
                self.append_chat_history(
                    {"role": "user", "content": completion_check_prompt}
                )

                completion_response = await self.model.chat(
                    history=self.chat_history,
                    tools=tools,
                    tool_choice="auto",
                    agent_name=self.__class__.__name__,
                )

                # # TODO: 压缩对话历史

                ## 没有调用工具，代表已经完成了
                if not (
                    hasattr(completion_response.choices[0].message, "tool_calls")
                    and completion_response.choices[0].message.tool_calls
                ):
                    logger.info("没有调用工具，代表任务已完成(多工具调用后)")
                    task_completed = True
                    return completion_response.choices[0].message.content
            else:
                logger.info("没有工具，代表任务完成")

            if retry_count >= self.max_retries:
                logger.error(f"超过最大尝试次数: {self.max_retries}")
                return f"Failed to complete task after {self.max_retries} attempts. Last error: {last_error_message}"

            if self.current_chat_turns >= self.max_chat_turns:
                logger.error(f"超过最大对话轮次: {self.max_chat_turns}")
                return f"Reached maximum number of chat turns ({self.max_chat_turns}). Task incomplete."

        logger.info(f"{self.__class__.__name__}:完成:执行子任务: {subtask_title}")

        return response.choices[0].message.content


# 长文本
# TODO: 并行 parallel
# TODO: 获取当前文件下的文件
# TODO: 引用cites tool
class WriterAgent(Agent):  # 同样继承自Agent类
    def __init__(
        self,
        task_id: str,
        model: LLM,
        max_chat_turns: int = 10,  # 添加最大对话轮次限制
        comp_template: CompTemplate = CompTemplate,
        format_output: FormatOutPut = FormatOutPut.Markdown,
        user_output: UserOutput = None,
    ) -> None:
        super().__init__(task_id, model, max_chat_turns, user_output)
        self.format_out_put = format_output
        self.comp_template = comp_template
        self.system_prompt = get_writer_prompt(format_output)
        self.available_images: list[str] = []

    async def run(
        self,
        prompt: str,
        available_images: list[str] = None,
        sub_title: str = None,
    ) -> str:
        """
        执行写作任务
        Args:
            prompt: 写作提示
            available_images: 可用的图片相对路径列表（如 20250420-173744-9f87792c/编号_分布.png）
            sub_title: 子任务标题
        """
        logger.info(f"subtitle是:{sub_title}")

        if available_images:
            self.available_images = available_images
            # 拼接成完整URL
            image_list = ",".join(available_images)
            image_prompt = f"\n可用的图片链接列表：\n{image_list}\n请在写作时适当引用这些图片链接。"
            prompt = prompt + image_prompt

        try:
            logger.info(f"{self.__class__.__name__}:开始:执行对话")
            self.current_chat_turns = 0  # 重置对话轮次计数器

            # 更新对话历史
            self.append_chat_history({"role": "system", "content": self.system_prompt})
            self.append_chat_history({"role": "user", "content": prompt})

            # 获取历史消息用于本次对话
            response = await self.model.chat(
                history=self.chat_history,
                agent_name=self.__class__.__name__,
                sub_title=sub_title,
            )
            response_content = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": response_content})
            logger.info(f"{self.__class__.__name__}:完成:执行对话")
            return response_content
        except Exception as e:
            error_msg = f"执行过程中遇到错误: {str(e)}"
            logger.error(f"Agent执行失败: {str(e)}")
            return error_msg

    async def summarize(self) -> str:
        """
        总结对话内容
        """
        try:
            self.append_chat_history(
                {"role": "user", "content": "请简单总结以上完成什么任务取得什么结果:"}
            )
            # 获取历史消息用于本次对话
            response = await self.model.chat(
                history=self.chat_history, agent_name=self.__class__.__name__
            )
            self.append_chat_history(
                {"role": "assistant", "content": response.choices[0].message.content}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"总结生成失败: {str(e)}")
            # 返回一个基础总结，避免完全失败
            return "由于网络原因无法生成详细总结，但已完成主要任务处理。"
