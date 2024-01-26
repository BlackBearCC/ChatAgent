import asyncio

from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Tongyi
from langchain.globals import set_verbose
from simpleaichat import prompt
import os

from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

os.environ["DASHSCOPE_API_KEY"] = "sk-dc356b8ca42c41788717c007f49e134a"
os.environ["OPENAI_API_KEY"] = "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"

user = "哥哥"
char = "兔叽"
history = "兔叽：你好啊，我是兔叽，你叫什么名字？"

entity_user_summary = ""
entity_char_summary = ""
user_info = "[兴趣:阅读], [性格:内向], [近期情感:正常]"
char_emotion = "[情绪状态:正常]"
char_info = f"[兴趣:无], [性格:内向，害羞], {char_emotion}，[生理状态:正常],[位置：客厅]，[动作：站立]"
reference = "None"
summary = ""


extracted_triplets = [("用户", "无明确需求")]
template = prompt.AGENT_ROLE_TEST
# template.format(user=user, char=char, history=history) # format the template
# 创建部分解析模板
prompt = PromptTemplate(
    template=template,
    input_variables=["input"],
    partial_variables={"user": user, "char": char,
                       "history": history, "user_info": user_info, "char_info": char_info,
                       "reference": reference, "summary": summary},
)
parser = StrOutputParser()
llm = Tongyi(model_name="qwen-max-1201")

chain = prompt | llm | parser


async def generate(input_content):
    async for chunk in chain.astream({"input": input_content}):
        print(chunk, end="")
while True:
    asyncio.run(generate(input("\nINPUT: ")))

# memory = ConversationBufferWindowMemory( k=1, return_messages=True)
# memory.save_context({"input": "hi"}, {"output": "whats up"})
# memory.save_context({"input": "not much you"}, {"output": "not much"})
# memory.load_memory_variables({})
