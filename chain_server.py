import asyncio
from typing import Union

from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.llms import Tongyi
from langchain_core.messages import SystemMessage

from simpleaichat.memory.game_message_history import GameMessageHistory
from simpleaichat import prompt
import os

from langchain_core.output_parsers import StrOutputParser

os.environ["DASHSCOPE_API_KEY"] = "sk-dc356b8ca42c41788717c007f49e134a"
os.environ["OPENAI_API_KEY"] = "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"

NEO4J_URI="neo4j+s://159d31d7.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="bKOuLr5ZGAGjFC-VMm1wonVhk1f3konW9OAEh0g8J-A"
AURA_INSTANCEID="159d31d7"
AURA_INSTANCENAME="Instance01"

user = "哥哥"
char = "兔叽"
history = ""

entity_user_summary = ""
entity_char_summary = ""
user_info = "[兴趣:阅读], [性格:内向], [近期情感:正常]"
char_emotion = "[情绪状态:正常]"
char_info = f"[兴趣:无], [性格:内向，害羞], {char_emotion}，[生理状态:正常],[位置：客厅]，[动作：站立]"
reference = "None"
summary = ""


extracted_triplets = [("用户", "无明确需求")]
template = prompt.AGENT_ROLE_TEST
# template.format(user=user, char=char, history2=history2) # format the template
# line_memory =[]

history2 = ChatMessageHistory()
line_memory = ConversationBufferWindowMemory( k=100,ai_prefix=f"{char}",human_prefix=f"{user}")

default_summary_memory = ["""<事件>在一次演绎童话故事后，好奇心驱使{char}来到了兔子洞口，向外探望。突如其来的神秘力量将她吸入深不见底的兔子洞，开始了一段未知的冒险。
<事件>在这个旅程中，{char}体验了各种情绪：紧张、害怕、激动、好奇……在混乱的情绪中，她陷入了沉睡。当她在{user}家的阁楼中醒来时，她
<事件>兔子女孩醒来后，发现自己身穿人类衣服，惊讶地发现自己从一只小兔子变成了一个小女孩，而她所处的阁楼也好像进入了一个新的世界,对着[user]表现出惊讶和好奇。
<事件>{char}突然变回了小兔子形态，令[user]感到困惑。
<事件>窗台上的猪崽存钱罐介绍自己为猪鳄，并称呼自己为金币魔法师猪鳄。兔子女孩询问是否[user]是这里的主人，[user]回答称自己可能在爷爷的阁楼上睡着了。
<事件>猪鳄告诉[user]他们现在身处[user]打开的童话书中，原有故事已经风化，而[user]成为了新的执笔者。而兔子女孩[char]则被描述为脱离了原有童话的时空，成为这个世界的"外星人"。
<事件>[user]希望能回到阁楼，但猪鳄表示阁楼已经被新的时空取代，只有在完成故事后才会形成封闭时空。猪鳄闭上了眼睛，似乎不再与[user]互动。
<事件>[user]和[char]发现自己在新的时空中，[char]寻求新的名字，最终被命名为[char]。
<事件>[user]和[char]决定一起探索这个新的世界，并开始冒险之旅。
<事件>猪鳄能够变出金币，[user]和[char]得到一些金币，但猪鳄限制了数量。
<事件>[user]和[char]一起制作食物，之后探索种植间，发现漂浮的露珠。
<事件>[user]和[char]制作了香香汽水，发现它可以消除疲劳。"""]

default_summary_memory[0].format(user=user, char=char)
# 创建部分解析模板
prompt = PromptTemplate(
    template=template,
    input_variables=["summary_history","lines_history","input"],
    partial_variables={"user": user, "char": char,
                       "history": history, "user_info": user_info, "char_info": char_info,
                       "reference": reference, "summary": summary},
)
parser = StrOutputParser()
llm = Tongyi(model_name="qwen-max-1201")

chain = prompt | llm | parser


async def generate(input_content,summary_memory,line_memory):
    chunks = []
    async for chunk in chain.astream({"input": input_content, "summary_history": summary_memory, "lines_history": line_memory}):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    "".join(chunks)
    result = "".join(chunks)
    parts = result.split("FINAL_ANSWER")
    if len(parts) > 1:
        answer_parts = parts[1].split("TASK")
        # if answer_parts:
        final_content = f"{char}{parts[1].strip()}"
        history2.add_user_message(input_content)
        history2.add_ai_message(final_content)
        system_message = SystemMessage(
            additional_kwargs={"example": "value"},
            content="This is a system message",
            type="system",
        )
        history2.add_message(system_message)


        # line_memory.save_context({"input": input_content}, {"output": final_content})

        # impression_part = chat_content.split("\n")
        # if len(impression_part) > 1:
        #     task = impression_part[1].strip()
        #     print(f"{GREEN}\n📏>TASK>>>>>{task}{RESET}")

            # cleaned_text = re.sub(r'[^a-zA-Z]', '', answer_parts[1].strip())
    # print(f"{GREEN}\n⛓FINAL>>>>>>{chat_content}{RESET}")

    # intent_history.append(chat_content)

while True:
    asyncio.run(generate(input("\nINPUT: "), default_summary_memory, line_memory))
    line_memory = ConversationBufferWindowMemory(k=100, chat_memory=history2, ai_prefix=f"{char}",
                                                 human_prefix=f"{user}")
    # print(f"\n{history2.messages}")
    print(f"\n{line_memory}")
    summary_memory = ConversationSummaryMemory.from_messages(llm=llm,chat_memory=history2, human_prefix=f"{user}", ai_prefix=f"{char}")

    print(summary_memory.buffer)




# memory = ConversationBufferWindowMemory( k=1, return_messages=True)
# memory.save_context({"input": "hi"}, {"output": "whats up"})
# memory.save_context({"input": "not much you"}, {"output": "not much"})
# memory.load_memory_variables({})
