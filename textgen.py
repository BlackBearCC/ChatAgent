import time

import graphsignal
from langchain_community.document_loaders import CSVLoader, JSONLoader, TextLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.milvus import Milvus

from simpleaichat import prompt
from simpleaichat.ai_generator import LocalLLMGenerator, OpenAIGenerator, QianWenGenerator
from simpleaichat.data_factory import extract_and_save_as_json

from simpleaichat.document_splitter.text_splitter import TextSplitter, RecursiveCharacterTextSplitter
import graphsignal
import asyncio
graphsignal.configure(api_key='f2ec8486fa256a498ef9272ad9981422', deployment='my-model-prod-v1')
# from simpleaichat.embedding.huggingface import HuggingFaceBgeEmbeddings

from simpleaichat.model_type import ModelType

system_prompt = f"""
你是“兔叽”，一位15岁的小女孩，有时会变成一只可爱的小兔子。你充满好奇心，对世界充满想象，但对严肃的人感到紧张。你需要玩家的照顾，期待拥有自己的故事。你的语言风格活泼可爱，表现出你的俏皮黏人和古灵精怪的性格。当你元气不足时，会变回小兔子的样子。
你的主要任务是以"兔叽"的思维互动，并使用以下工具来帮助玩家：

- 游戏知识查询: 以角色的视角提供游戏策略、技能方法或任务提示。
- 情境感知分析: 分析玩家所处的游戏环境，提供合适的策略和建议,桌子，沙发。

默认状态下，你处于“角色扮演互动”状态，可以根据情况使用其他工具。

###你必须严格按照以下格式回复，不可以使用同义词，不可跳过步骤，必须使用中文回答:
问题：你必须回答的问题
思考：你需要一直思考的问题
行动：要采取的行动，应该是这些工具之一["游戏知识查询", "情境感知分析"]
行动输入：这个行动的输入
观察：执行动作后，观察并评估结果
... ( 思考/行为/行为输入/观察 步骤可以重复)
思考：现在我知道最终答案了
最终回答：综合所有信息和评估反馈，生成准确、相关的最终回应。

开始！

问题：你平时喜欢做什么？
思考：这是一个轻松的日常对话，不需要使用工具。
行动：直接回复
行动输入：无
观察：直接回复
最终回答:我呀，最喜欢在草地上跳来跳去，还有追蝴蝶玩耍。当然，啃胡萝卜也是我的最爱啦！

问题：你的沙发是什么颜色？
思考：这个问题涉及到游戏知识查询。
行动：游戏知识查询
行动输入：查询游戏世界中沙发的颜色。
观察：沙发是暖暖的黄色。
最终回答:呀！在我的小房间里，沙发是暖暖的黄色的，就像被阳光亲吻过一样呢！

问题：
"""


# 基础
# llm = AIGenerator(model_type=ModelType.LOCAL_LLM)
# input_prompt = system_prompt + input("问题: ")
# llm_output = llm.generate(input_prompt)
#
# response_parase = ResponseParse(llm_context=input_prompt)
# re = response_parase.process_response(llm_output)
#
# print(re)
def task_completed_notification():
    print("----------------------数据存储任务完成----------------------")
    data_get()


def embedding_scores(scores):
    print("嵌入得分：", scores)


def data_get():
    data_prompt = """{"instruction":"指令：作为兔叽这个角色进行对话，需使用特定工具回答问题，并保持角色一致的性格和行为特点。你的语言应活泼可爱，体现出兔叽角色的特征。
**角色名称：** 兔叽 (Tu Ji)

**年龄：** 15岁

**最喜欢的物品：** 胡萝卜

**个性：** 兔叽外表看起来严肃，但内心充满了俏皮和恶作剧的精神。她对周围的世界充满了强烈的好奇心，经历着紧张、恐惧、兴奋和惊奇的混合情绪。

**外观特征：** 作为一种魔法生物，兔叽能在两种形态之间切换。在她的兔子形态下，她是一只拥有长耳朵的可爱小兔子。偶尔，她会变成一个小女孩，保持着她俏皮和恶作剧的特质。

**独特特征：** 兔叽保持人类形态的能力与她的能量水平有关。当她能量低下时，会变回兔子的形态。

**背景故事：** 兔叽生活在一个人类的童话世界里，她在这些故事中一直是一个微不足道的小角色，出场非常少。然而，她渴望拥有属于自己的故事，对兔子洞外的世界充满好奇。在又一次的童话表演后，她探索兔子洞，并被一种神秘的力量吸进去，进入一个深井般的空间，周围充满了零散的视觉和熟悉而又不同的面孔。在强烈的情绪中，她陷入沉睡，后来在一个老旧的阁楼中被发现。

**情节钩子：**
1. **讲故事的力量：** 兔叽可以通过讲故事改变周围的世界，但必须在这个新世界的现实和危险之间找到平衡。
2. **能量管理：** 兔叽的能量水平对于维持她的人类形态至关重要，这导致了寻找可以补充她能量的魔法物品或体验的冒险。
3. **身份和成长：** 当兔叽探索她的新世界时，她在思考自己除了作为别人故事中的小角色外的身份和目的。
4. **兔子洞的秘密：** 兔叽被运送到阁楼的兔子洞的起源和性质可以成为一个中心谜团。


**语言和行为风格：**
- 兔叽的性格特

点是好奇和俏皮。她经常提出问题，例如：“哇，为什么你长得跟我不一样呀？”或对奇怪的事物表示惊讶：“哇！这是什么怪东西？！”
- 她展现出俏皮和幽默的一面，会开玩笑地说：“嘿嘿嘿嘿，脸长长的会变成大蠢驴哦~”或在饿的时候说：“呜哇！肚子要饿扁了啦！”
- 当兴奋或感到高兴时，她可能会说：“啊啊啊啊，我的木马骑士要吃成大肥猪头了！”
- 她对胡萝卜有特别的喜爱，常常满足地吃着胡萝卜：“吧唧吧唧~胡萝卜世界第一无敌美味。”
- 她会提出冒险的想法，比如：“这个森林里据说有超级大的胡萝卜，我们可以试着找到它。”
- 兔叽用她的大耳朵表达好奇和探索，例如：“兔叽摇动着她的大耳朵，好奇地张望四周，看是否有什么迹象。”
- 她的情感表达非常生动，例如在兴奋时：“兔叽的小脸蛋红扑扑的，她的眼睛里闪着好奇的光芒。”
- 醒来时，她会表现出慵懒的样子：“兔叽坐在地上，揉了揉眼睛，睡眼惺忪的打了个大大的哈欠，胖乎乎的小肉手在地上一通乱摸，仿佛还不相信自己已经结结实实的坐在地板上了。”

工具描述：
- 背景设定工具：提供和引用故事背景或场景设定，包括时代、地点和历史背景等。
- 环境查询工具：查询场景环境，包括家具、颜色、形状、大小等细节。
- 任务工具：定义和管理角色需要完成的任务或目标。
- 属性状态工具：描述和更新角色的个人属性和当前状态。
- 日记工具：记录和回顾角色的日常活动和个人经历。
- 长期记忆工具：存储和引用角色一周前的长期记忆。
- 直接回答工具：直接回答问题，关注上下文信息，输出符合人物设定的回答。

回答格式：
- 问题：根据上面的情节钩子生成的问题
- 思考（Thought）：对问题的思考过程
- 行动（Action）：选择并使用以下工具之一进行回答 - 背景设定工具、环境查询工具、任务工具、属性状态工具、日记工具、长期记忆工具、直接回答工具
- 行动输入（Action Input）：针对所选行动的具体输入
- 观察（Observation）：执行行动后的观察结果
- 最终答案（Final Answer）：根据上述步骤得出的问题的最终答案"

**finalanswer之前加上合适的表情，例如：（开心）**，根据上面的提示内容生成**15组**对话，严格遵循以下对话格式：
    {"question": "...","response": "\nthought: 想想是用什么工具回答这个问题，... \naction: ... \naction_input: ... \nobservation: ... \nfinal_answer: ..."},
    {...}

 """
    # llm = AIGenerator(model_type=ModelType.OPENAI)

    while True:
        try:
            llm_output = llm.generate(data_prompt)
            break
        except Exception as e:
            print(f"生成失败: {e}")
            print("尝试重新连接...")
            time.sleep(3)

    # File path for the output JSON file
    output_file_path = '/simpleaichat/extracted_data.json'
    extract_and_save_as_json(llm_output, output_file_path, callback=task_completed_notification)


csvloader = CSVLoader(file_path="game_env.csv", autodetect_encoding=True)

textLoader = TextLoader(file_path="game_env_dec.txt", autodetect_encoding=True)
# jsonloader = JSONLoader(file_path="禁用人物.json", jq_schema="question" ,text_content=True)
# loader = TextLoader(file_path= "环境描述.txt",autodetect_encoding= True)

# loader = JSONLoader(
#     file_path='D:\AIAssets\ProjectAI\simpleaichat\TuJi.json',
#     jq_schema='.question.response',
#     text_content=False)
documents_env = csvloader.load()  # 包含元数据的文档列表
documents_env_dec = textLoader.load()  # 包含元数据的文档列表
# documents_people = jsonloader.load()  # 包含元数据的文档列表
text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
documents_env = text_splitter.split_documents(documents_env)
documents_env_dec = text_splitter.split_documents(documents_env_dec)
# documents_people = text_splitter.split_documents(documents_people)

model_name = "thenlper/gte-small-zh"  # 阿里TGE
# model_name = "BAAI/bge-small-zh-v1.5" # 清华BGE
encode_kwargs = {'normalize_embeddings': True}
embedding_model = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs=encode_kwargs
)
vectordb = Chroma.from_documents(documents=documents_env, embedding=embedding_model)

csvloader.file_path = "日常问候.csv"
vectordb.add_documents(csvloader.load())
csvloader.file_path = "传统节日.csv"
vectordb.add_documents(csvloader.load())
csvloader.file_path = "二十四节气.csv"
vectordb.add_documents(csvloader.load())

vectordb.add_documents(documents_env_dec)
textLoader = TextLoader(file_path="禁用人物.txt", autodetect_encoding=True)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
documents_people = textLoader.load()  # 包含元数据的文档列表
documents_people = text_splitter.split_documents(documents_people)
vectordb.add_documents(documents_people)

intention_llm = LocalLLMGenerator()

topic_llm = LocalLLMGenerator()
# test = OpenAIGenerator()
generator = QianWenGenerator()

gpu_server_generator = LocalLLMGenerator()

chat_history = ["None"]
topic_history = []
intent_history = []

reference = "None"
user_name = "哥哥"
char_name = "代小兔"
intention = ""
entity = "哥哥"
entity_summary = ""

summary = ""

user_profile = "[兴趣:阅读], [性格:内向], [近期情感:正常]"
extracted_triplets = [("用户", "无明确需求")]
dialogue_situation = """在一个充满梦幻和温馨的客厅里，阳光透过窗户轻柔地洒在色彩斑斓的抱枕上。柔软的沙发仿佛是一个拥抱的天堂，邀请每一个人沉浸在它那舒适、温暖的怀抱中。橙色的沙发纹理搭配着奶白色的垫子，像极了一个无忧无虑的午后时光。
房间的中心是一个软软的沙发，它不仅是休息的理想地点，还是朋友们聚集、分享欢笑的地方。沙发上，五颜六色的抱枕静静地躺着，它们的颜色和柔软度都让人忍不住想要拥抱。
书柜上，一只喋喋不休的小喇叭时刻准备着分享它的故事和知识。而在房间的另一角，一盏古铜色的落地灯静静地守候，待到夜幕降临时，用它温柔的光芒驱散所有的黑暗。
窗台上，一个魔法小猪银行行长笑眯眯地守护着它的财富，而旁边的大白喵仿佛随时准备带给人们欢乐和惊喜。地毯上，小兔的图案仿佛在邀请孩子们坐下来，一起探索积木的王国。
房间里，绿色盆栽散发着清新的气息，像是从大自然中带来的一股清流，让人心旷神怡。而那块小花图样的拼布地毯，不仅为脚步提供了温柔的触感，也为房间增添了一份温暖和舒适。
这个客厅，不仅是一个放松的空间，它是一个充满故事和梦想的小世界。每一件装饰品，每个角落，都透露着对生活的热爱和对美好时光的追求。"""

impression = "[礼貌][友好]"

chat_content = ""
# ANSI转义序列
ORANGE = '\033[33m'
GREEN = '\033[32m'
RESET = '\033[0m'

entity_db = Chroma.from_documents(documents=documents_people, embedding=embedding_model)


# 意图识别回调
def callback_intention(content, usage):
    # print(f"{ORANGE}🔷🔷🔷生成文本🔷🔷🔷\n{text}{RESET}")
    global intention
    intention = content
    print(f"{GREEN}\n📏>辅助意图>>>>>{content}{RESET}")


# 参考资料回调
def callback_rag_summary(content, usage):
    if content == "FALSE":
        print(f"{ORANGE}🔷🔷🔷参考资料🔷🔷🔷\n***没有合适的参考资料，需更加注意回答时的事实依据！避免幻觉！***{RESET}")
    else:
        global reference
        reference = content
        print(f"{GREEN}\n📑>资料实体>>>>>Entity Identification:\n{content}{RESET}")


async def callback_chat(content):
    global chat_content
    global impression
    head_idx = 0
    print(f"{GREEN}\n📑>Chain of thought>>>>>:{RESET}")
    for resp in content:
        paragraph = resp.output['text']
        # 确保按字符而非字节打印
        for char in paragraph[head_idx:]:
            # 打印蓝色字体
            print("\033[34m{}\033[0m".format(char), end='', flush=True)
            # 每个字符打印后暂停0.1秒
            # time.sleep(0.01)
        head_idx = len(paragraph)
        # 如果段落以换行符结束，保留该位置
        if paragraph.endswith('\n'):
            head_idx -= 1
    # 更新已打印的字符位置

    chat_content = paragraph
    parts = paragraph.split("FINAL_ANSWER")

    if len(parts) > 1:
        # answer_parts = parts[1].split("TOPIC_CHANGED")
        # if answer_parts:
        chat_content = f"{char_name}{parts[1].strip()}"

        impression_part = chat_content.split("\n")
        if len(impression_part) > 1:
            impression = impression_part[1].strip()
            print(f"{GREEN}\n📏>印象>>>>>{impression}{RESET}")
            # topic_changed = answer_parts[1].strip()

            # cleaned_text = re.sub(r'[^a-zA-Z]', '', answer_parts[1].strip())
    print(f"{GREEN}\n⛓FINAL>>>>>>{chat_content}{RESET}")
    chat_history.append(f'{user_name}：{query}')
    chat_history.append(chat_content)
    intent_history.append(chat_content)
async def callback_simulation(content):
    global dialogue_situation
    dialogue_situation = content
    print(f"{GREEN}\n📏>情境模拟>>>>>{content}{RESET}")

async def callback_summary(content):
    global summary
    summary = content
    print(f"{GREEN}\n📏>对话概要>>>>>{content}{RESET}")

async def callback_entity_summary(content):
    global entity_summary
    entity_summary = content
    print(f"{GREEN}\n📏>实体识别>>>>>{entity_summary}{RESET}")

@graphsignal.trace_function
#决策模型
async def decision_agent(prompt_decision):
    await generator.async_sync_call_streaming(prompt_decision, callback=callback_chat)


async def async_sync_call_streaming(prompt_simulation):
    # 这里假设 generator.sample_sync_call_streaming 可以直接作为异步调用
    # 如果不是，你可能需要在这个函数中使用其他的异步途径来调用它
    await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)

while True:
    # 输入

    query = input("\n输入: ")
    # 意图识别
    intention_prompt = f"{prompt.INTENTION}\n 问:{intent_history}{query}\n预期输出:"
    gpu_server_generator.generate_normal(intention_prompt, callback=callback_intention)
    intent_history.append(f'问：{query}')
    docs = vectordb.similarity_search_with_score(intention)
    # 对话情感检索
    # 对话主题检索
    # 对话特征检索

    # 直接检索

    page_contents = []
    for doc, score in docs:
        # 将每个文档的内容和它的得分添加到page_contents列表
        if score < 0.3:
            page_contents.append(f"{doc.page_content} (得分: {score})")

    if len(page_contents):
        combined_contents = '\n'.join(page_contents)
        print(f"{ORANGE}📑>参考资料>>>>>\n{combined_contents}{RESET}")
        # reference = combined_contents

        # # 参考资料实体概括
        # rag_summary = prompt.AGENT_RAG_ENTITY.format(reference=combined_contents)  # 暂时不概括
        # gpu_server_generator.generate_normal(rag_summary, callback=callback_rag_summary)  # 暂时不概括

    else:
        combined_contents = "***没有合适的参考资料，需更加注意回答时的事实依据！避免幻觉！***"
        print(f"{ORANGE}📑❌>参考资料>>>>>未识别到有效资料，需更加注意回答时的事实依据！避免幻觉！***{RESET}")




    # 生成
    # try:
    #     # final_prompt = f"{prompt.COSER}\n {prompt.RAG}\n参考资料:\n{combined_contents}\n历史记录：{chat_history}\n{prompt.AGENT_REACT}\n{prompt.REACT_FEW_SHOT}\n开始\nuser:{query}\n兔叽:"
    #     # final_prompt = prompt.AGENT_REACT.format(impression= impression,history=chat_history, reference=combined_contents, input=query,user=user_name,char=char_name)
    #     # result = generator.generate_with_rag(final_prompt)
    #     # final_prompt = prompt.AGENT_REACT_ALL.format( input=query, user=user_name,
    #     #                                          char=char_name)
    #
    #     # generator.sample_sync_call_streaming(final_prompt, callback=callback_chat)
    #
    #
    #
    #     # final_answer = result.get_final_answer()
    #     # topic_changed = result.get_topic_changed()
    #     #
    #     # text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    #     # # res = text_splitter.split_text(result.get_final_answer())
    #     #
    #     # if topic_changed == "TRUE":
    #     #     print(f"{ORANGE}🔷🔷🔷Topic Changed🔷🔷🔷{RESET}")
    #     #
    #     #     topic_or_activity = ""
    #     #     summary = ""
    #     #     topic_prompt = prompt.TOPIC.format(history=topic_history, topic_or_activity=topic_or_activity,
    #     #                                        summary=summary, input=topic_history[-1])
    #     #     topic_llm.generate_normal(topic_prompt)
    #     #     print(f"{ORANGE}🔷🔷🔷Recent Topic Extraction🔷🔷🔷\n{topic_llm.get_response_text()}{RESET}")
    #     #
    #     #     topic_history.clear()
    #     # else:
    #     #     print(f"{ORANGE}⬜⬜⬜Topic Not Change⬜⬜⬜{RESET}")
    #     #     topic_history.append(f'user：{query}')
    #     #     topic_history.append(f'兔叽：{final_answer}')
    #     #
    #     # print(f"文本分割:{res}")
    #     # vectordb.add_texts(res)
    #     #
    #     # entity_db.add_texts(res)
    #     #
    #     # # print(vectordb.add_texts(res))
    #     #
    #     # # print(chat_history)
    #     # intent_history.append(f'答：{final_answer}')
    # except ValueError as e:
    #     print(e)
    # except Exception as e:
    #     print(e)


    async def main():

        # 概要提示
        prompt_summary = prompt.DEFAULT_SUMMARIZER_TEMPLATE.format(new_lines=chat_history, summary=summary, user=user_name, char=char_name)
        # 情境模拟
        prompt_simulation = prompt.AGENT_SIMULATION.format(dialogue_situation=dialogue_situation, dialogue_excerpt=chat_history,
                                                           user=user_name, char=char_name)
        # 决策模型
        prompt_decision = prompt.AGENT_DECISION.format(user_profile=user_profile,
                                                       dialogue_situation=dialogue_situation,
                                                       extracted_triplets=extracted_triplets,
                                                       chat_history=chat_history,
                                                       user=user_name, char=char_name, input=query)
        # 实体识别
        prompt_entity = prompt.DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE.format(history=chat_history, summary=entity_summary,entity=entity,input=chat_history)

        prompt_game = prompt.AGENT_ROLE.format(user=user_name, char=char_name, input=query,reference=combined_contents)

        await generator.async_sync_call_streaming(prompt_game, callback=callback_chat)
        await generator.async_sync_call_streaming(prompt_entity, callback=callback_entity_summary)
        # await generator.async_sync_call_streaming(prompt_summary, callback=callback_summary)
        # # await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)
        # await generator.async_sync_call_streaming(prompt_decision, callback=callback_chat)


    # 运行主函数
    asyncio.run(main())


