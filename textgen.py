# -*- coding:utf-8 -*-
import time

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores.chroma import Chroma

from app import prompt
from app.ai_generator import LocalLLMGenerator, QianWenGenerator
from app.data_factory import extract_and_save_as_json

from app.utils.document_splitter.text_splitter import RecursiveCharacterTextSplitter
import graphsignal
import asyncio

from app.database.leo_neo4j_graph import DatabaseConfig, Leo_Neo4jGraph

graphsignal.configure(api_key='f2ec8486fa256a498ef9272ad9981422', deployment='my-model-prod-v1')

from langchain_community.graphs.graph_document import GraphDocument
from langchain_community.graphs.graph_document import Node, Relationship

from langchain_core.documents import Document

from app.models import UserProfile
from app.models import CharacterProfile
import re  # 导入 re 模块
from langchain_community.llms import Tongyi
from app.utils.data_loader import DataLoader
import json
from app.core.prompts.tool_prompts import search_helper, search_graph_helper
from fastapi import FastAPI


def split_text(documents, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)


def embedding_scores(scores):
    print("嵌入得分：", scores)

    while True:
        try:
            llm_output = llm.generate(data_prompt)
            break
        except Exception as e:
            print(f"生成失败: {e}")
            print("尝试重新连接...")
            time.sleep(3)

    # File path for the output JSON file
    output_file_path = 'app/extracted_data.json'
    extract_and_save_as_json(llm_output, output_file_path, callback=task_completed_notification)


import databases

DATABASE_URL = "mysql+mysqlconnector://<username>:<password>@<host>/<dbname>"
database = databases.Database(DATABASE_URL)
# metadata = sqlalchemy.MetaData()


app = FastAPI()
# Base = declarative_base()

query = ""
data_config = DatabaseConfig("config.ini")
try:
    graphdb = Leo_Neo4jGraph(data_config.neo4j_uri, data_config.neo4j_username, data_config.neo4j_password)
except Exception as e:
    print(e)

documents_env = DataLoader("game_env.csv").load()
documents_env_dec = DataLoader("game_env_dec.txt").load()

documents_env = split_text(documents_env, 50, 10)
documents_env_dec = split_text(documents_env_dec, 50, 10)

model_name = "thenlper/gte-small-zh"  # 阿里TGE
# model_name = "BAAI/bge-small-zh-v1.5" # 清华BGE
encode_kwargs = {'normalize_embeddings': True}
embedding_model = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs=encode_kwargs
)
vectordb = Chroma.from_documents(documents=documents_env, embedding=embedding_model)

files = ["日常问候.csv", "传统节日.csv", "二十四节气.csv", "禁用人物.txt"]

for file in files:
    documents = DataLoader(file).load()
    vectordb.add_documents(documents)

intention_llm = LocalLLMGenerator()

topic_llm = LocalLLMGenerator()
# test = OpenAIGenerator()
generator = QianWenGenerator()

gpu_server_generator = LocalLLMGenerator()

from app.service.service import *

# 假设的会话ID
session_id = "123"

# 调用服务层函数
user_profile, character_profile = get_user_and_character_profiles(session_id)
dialogue_manager = get_dialogue_manager_service(session_id)
print(update_dialogue_summary_service(session_id, "概要测试"))
print(get_dialogue_summary_service(session_id))
print(update_dialogue_situation_service(session_id, "情境测试"))
print(get_dialogue_situation_service(session_id))

print(dialogue_manager.situation)

# 使用获取到的数据
if user_profile and character_profile:
    print("User Name:", user_profile.name)
    print("Character Name:", character_profile.name)

from app.service.service import *

# extracted_triplets = [("用户", "无明确需求")]
default_dialogue_situation = """
背景和环境：
在一个温馨的客厅内，阳光透过窗户洒下，将整个空间渲染成温暖的色调。客厅里摆放着柔软的沙发和色彩斑斓的抱枕，创造出一个放松和舒适的环境。不仅如此，房间中还布满了梦幻般的装饰：小喇叭、古铜色落地灯、魔法小猪银行，以及充满童趣的大白喵和小兔图案地毯。这不仅是一个客厅，更像是一个充满故事和梦想的小世界。
对话内容摘要：
在这次冒险的开始，{char}和{user}在充满梦幻的客厅中相遇。{char}，原是一个童话世界中的小配角，通过神秘力量进入了{user}所在的世界。在这个全新的环境中，{char}表现出好奇和激动，而{user}则显得有些困惑但也乐于接受这个意外的伙伴。经过一系列的互动和探索，他们建立了友谊，并一起制作食物、探索种植间，发现了漂浮的露珠，并用它制作了神奇的香香汽水。
角色设定和特性：
{char}：好奇心强，充满活力，渴望冒险和新经历。作为原童话故事中的小配角，{char}希望在新的世界中成为主角，并探索属于自己的故事。
{user}：冷静，理性，适应能力强。作为现实世界中的普通人，{user}意外地接受了{char}和新的冒险，展现出悠闲和适应的态度。
{user}行为和情绪倾向：
{user}在整个互动过程中保持着开放和接纳的心态。尽管{char}的突然出现和奇妙的事件让{user}感到惊讶，但他还是愿意接纳并帮助{char}适应这个新世界。在制作食物和探索种植间的过程中，{user}展现了领导和关怀的一面，引导{char}发现新事物，并一起解决问题。
当前对话的关键点和目标：
当前对话的关键点在于加强{char}和{user}之间的友情，共同探索这个新世界，并为接下来的冒险奠定基础。目标是让{char}更好地适应新环境，同时让{user}更加了解{char}的性格和需求。通过这次互动，他们可以发现更多关于这个新世界的秘密，并准备好面对即将到来的挑战和冒险。"""

impression = "[礼貌][友好]"

prompt_test = prompt.prompt_test.format(char=character_profile.name, user=user_profile.name)

# ANSI转义序列
ORANGE = '\033[33m'
GREEN = '\033[32m'
RESET = '\033[0m'

dialogue_manager.situation = default_dialogue_situation.format(char=character_profile.name, user=user_profile.name)


# 意图识别回调
def callback_intention(content, usage):
    # print(f"{ORANGE}🔷🔷🔷生成文本🔷🔷🔷\n{text}{RESET}")
    # global intention
    typewriter(content)
    dialogue_manager.intention = content

    # print(f"{GREEN}\n📏>辅助意图>>>>>{content}{RESET}")


# 参考资料回调
def callback_rag_summary(content, usage):
    if content == "FALSE":
        print(f"{ORANGE}🔷🔷🔷参考资料🔷🔷🔷\n***没有合适的参考资料，需更加注意回答时的事实依据！避免幻觉！***{RESET}")
    else:
        global reference
        reference = content
        print(f"{GREEN}\n📑>资料实体>>>>>Entity Identification:\n{content}{RESET}")


async def callback_knowledge_graph(content):
    # global testText
    # testText = content
    full_content = await typewriter(content)
    # npcName= "红心皇后"
    # query = f"""
    # MATCH (n)-[r]->(m)
    # WHERE n.npcName = '{npcName}'
    # RETURN n, r, m
    # LIMIT 10
    # """
    document_source = Document(
        page_content="动态游戏信息",
        metadata={"author": "leozy", "date": "2024"}
    )
    # result = graphdb.query(query)

    # user = Node(id="大头", type="user", properties={"name": "大头"})
    # charactor = Node(id="兔叽", type="charactor", properties={"name": "兔叽"})
    # friendship = Relationship(source=user, target=charactor, type="FRIENDS_WITH", properties={"since": "2024"})
    # graph_doc = GraphDocument(nodes=[user, charactor], relationships=[friendship], source=document_source)

    graph_document = process_entities_and_relationships(full_content)
    graphdb.add_graph_documents([graph_document])
    print(f"{GREEN}\n📑>图谱>>>>>:\n{full_content}{RESET}")


def clean_json_data(data: str) -> str:
    """
    清理 JSON 数据字符串，移除多余的字符。
    :param data: 原始数据字符串。
    :return: 清理后的字符串。
    """
    # 移除可能的多余字符，例如：```json 和 ```
    data = re.sub(r'^\s*```json\s*|\s*```\s*$', '', data, flags=re.MULTILINE)
    # 处理其他可能的格式问题（根据实际情况添加）
    # ...
    print(data)
    return data


def process_entities_and_relationships(data: str) -> GraphDocument:
    try:
        # 清理数据并解析 JSON
        clean_data = clean_json_data(data)
        data_dict = json.loads(clean_data)

        # 提取实体和关系
        entities_data = data_dict.get("实体", [])
        relationships_data = data_dict.get("关系", [])

        # 创建节点对象
        nodes = {entity['id']: Node(id=entity['id'], type=entity['type'], properties={"name": entity['name']})
                 for entity in entities_data}

        # 创建关系对象
        relationships = []
        for rel in relationships_data:
            source_node = nodes.get(rel['source_id'])
            target_node = nodes.get(rel['target_id'])
            if source_node and target_node:
                relationships.append(Relationship(source=source_node, target=target_node, type=rel['type']))

        # 创建文档来源
        document_source = Document(page_content="动态游戏信息", metadata={"author": "leozy", "date": "2024"})

        # 创建并返回 GraphDocument 对象
        print("图谱构建完成---------")
        return GraphDocument(nodes=list(nodes.values()), relationships=relationships, source=document_source)
    except json.JSONDecodeError as e:
        raise ValueError(f"解析 JSON 时出错：{e}")


import langchain.callbacks as callbacks
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


##通义流式传输失败
async def generate_stream(llm, prompt, **kwargs):
    async for chunk in llm.generate(
            prompts=["Generate a story about a cat named Mittens."],
            max_tokens=100,
            stream=True
    ):
        print(chunk)


from colorama import Fore, Style


class ChatCallbackHandler(BaseCallbackHandler):
    def on_text(self, text, **kwargs):
        # 修改字体颜色
        print(Fore.RED + text + Style.RESET_ALL)

    def on_llm_end(self, response, **kwargs):
        # 调用你想要执行的函数
        # parser = LLMResultParser()

        print({"response": response})


async def update_entity():
    # 实体识别
    llm = Tongyi(model_name="qwen-max-1201", top_p=0.1, dashscope_api_key="sk-dc356b8ca42c41788717c007f49e134a")
    entity_template = prompt.DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE
    entity_prompt = PromptTemplate(template=entity_template, input_variables=["history", "summary", "entity", "input"])
    callback_handler = ChatCallbackHandler()
    output_parser = StrOutputParser()
    entity_chain = LLMChain(llm=llm, prompt=entity_prompt, output_parser=output_parser)
    entity_input = {"history": dialogue_manager.chat_history,
                    "summary": dialogue_manager.entity_summary,
                    "entity": dialogue_manager.user_name,
                    "input": dialogue_manager.chat_history}
    entity_result = await entity_chain.ainvoke(entity_input, callbacks=[callback_handler])
    entity_text = entity_result["text"]

    print(f'{GREEN}\n📏>实体更新>>>>>{entity_text}{RESET}')


async def update_summary(session_id):
    # 对话概要
    llm = Tongyi(model_name="qwen-max-1201", top_p=0.1, dashscope_api_key="sk-dc356b8ca42c41788717c007f49e134a")
    summary_template = prompt.DEFAULT_SUMMARIZER_TEMPLATE
    summary_prompts = PromptTemplate(template=summary_template,
                                     input_variables=["new_lines", "summary", "user", "char"])
    output_parser = StrOutputParser()
    summary_chain = LLMChain(llm=llm, prompt=summary_prompts, output_parser=output_parser)
    summary_input = {"new_lines": dialogue_manager.chat_history,
                     "summary": dialogue_manager.summary,
                     "user": user_info.name,
                     "char": char_info.name}
    summary_result = await summary_chain.ainvoke(summary_input)
    summary_text = summary_result["text"]
    update_dialogue_summary_service(session_id, summary_text)
    print(f'{GREEN}\n📏>对话概要>>>>>{summary_text}{RESET}')


async def on_update_situation_complete():
    # 这里是回调函数，你可以在这里添加当 update_situation() 完成时需要执行的代码
    print("Update situation completed")


async def update_situation(callback):
    # 情境模拟
    llm = Tongyi(model_name="qwen-max-1201", top_p=0.1, dashscope_api_key="sk-dc356b8ca42c41788717c007f49e134a")
    situation_template = prompt.AGENT_SITUATION
    situation_prompt = PromptTemplate(template=situation_template,
                                      input_variables=["dialogue_situation", "dialogue_excerpt", "user", "char"])
    situation_chain = LLMChain(llm=llm, prompt=situation_prompt, output_parser=StrOutputParser())
    situation_input = {"dialogue_situation": dialogue_manager.situation,
                       "dialogue_excerpt": dialogue_manager.chat_history,
                       "user": dialogue_manager.user_name,
                       "char": dialogue_manager.char_name}
    situation_result = await situation_chain.ainvoke(situation_input)
    situation_text = situation_result["text"]
    print(f'{GREEN}\n📏>情境模拟>>>>>{situation_text}{RESET}')
    await callback()
    update_dialogue_situation_service(session_id, situation_text)


async def update_emotion(session_id):
    # 情绪
    llm = Tongyi(model_name="qwen-max-1201", top_p=0.1, dashscope_api_key="sk-dc356b8ca42c41788717c007f49e134a")
    emotion_template = prompt.AGENT_EMOTION
    emotion_prompt = PromptTemplate(template=emotion_template,
                                    input_variables=["emotion", "dialogue_situation", "history", "char"])
    emotion_chain = LLMChain(llm=llm, prompt=emotion_prompt, output_parser=StrOutputParser())
    emotion_input = {"emotion": char_info.emotional_state,
                     "dialogue_situation": dialogue_manager.situation,
                     "history": dialogue_manager.chat_history,
                     "char": char_info.name}
    emotion_result = await emotion_chain.ainvoke(emotion_input)
    emotion_text = emotion_result["text"]
    # char_info.emotional_state = emotion_text
    update_character_emotion_service(session_id, emotion_text)
    print(f'{GREEN}\n📏>情绪更新>>>>>{emotion_text}{RESET}')


async def callback_chat(content):
    task = ""
    head_idx = 0
    # print(f"{GREEN}\n📑>Chain of thought>>>>>:{RESET}")
    # print(f"{GREEN}🎮>GameData(sample)>>>>>:{char_info}{RESET}")
    # for resp in content:
    #     paragraph = resp.output['text']
    #     # 确保按字符而非字节打印
    #     for char in paragraph[head_idx:]:
    #         # 打印蓝色字体
    #         print("\033[34m{}\033[0m".format(char), end='', flush=True)
    #         # 每个字符打印后暂停0.1秒
    #         # time.sleep(0.01)
    #     head_idx = len(paragraph)
    #     # 如果段落以换行符结束，保留该位置
    #     if paragraph.endswith('\n'):
    #         head_idx -= 1
    # 使用正则表达式提取JSON部分
    # 将字节对象解码为字符串
    decoded_text = content.decode('utf-8')
    search_pattern = '"finish_reason":"stop"'
    if search_pattern in decoded_text:
        result = "匹配成功，流式传输停止：'finish_reason:stop'."
        # 提取JSON字符串
        json_str = decoded_text.split('data:', 1)[1].strip()
        # 转换为JSON对象
        try:
            data_json = json.loads(json_str)
            # print(data_json['output']['text'])
            ai_message = data_json['output']['text']
            # 按照 "FINAL_ANSWER" 拆分
            content_parts = ai_message.split("FINAL_ANSWER")
            if len(content_parts) > 1:
                # 如果存在 "TASK"，按 "TASK" 进一步拆分
                task_parts = content_parts[1].split("TASK", 1)
                # 过滤 ";" 和 ":"
                final_answer_content = re.sub(r'[;:]', '', task_parts[0].strip())
            else:
                final_answer_content = ""
            print(f"{GREEN}\n⛓FINAL>>>>>>{final_answer_content}{RESET}")
            await update_entity()

            dialogue_manager.chat_history.append(f'{user_info.name}:{query}')
            dialogue_manager.chat_history.append(f'{char_info.name}:{final_answer_content}')
        except json.JSONDecodeError:
            print("JSON解析错误")
            data_json = {}

    else:
        result = "匹配失败，流式传输中。"
    # print(decoded_text)
    # print(result)

    # chat_content = paragraph
    # parts = paragraph.split("FINAL_ANSWER")
    # if len(parts) > 1:
    #     answer_parts = parts[1].split("TASK")
    #     # if answer_parts:
    #     chat_content = f"{char_info.name}{parts[1].strip()}"
    #
    #     impression_part = chat_content.split("\n")
    #     if len(impression_part) > 1:
    #         task = impression_part[1].strip()
    #         print(f"{GREEN}\n📏>TASK>>>>>{task}{RESET}")
    #
    #         # cleaned_text = re.sub(r'[^a-zA-Z]', '', answer_parts[1].strip())
    # # print(f"{GREEN}\n⛓FINAL>>>>>>{chat_content}{RESET}")
    # dialogue_manager.chat_history.append(f'{user_info.name}：{query}')
    # dialogue_manager.chat_history.append(chat_content)
    # dialogue_manager.intent_history.append(chat_content)
    # if "记忆更新" in task:
    #     # 概要提示
    #     # prompt_summary = prompt.DEFAULT_SUMMARIZER_TEMPLATE.format(new_lines=chat_history, summary=summary,
    #     #                                                            user=user_name, char=char_name)
    #     # 实体识别
    #     prompt_entity = prompt.DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE.format(history=dialogue_manager.chat_history,
    #                                                                         summary=f"{dialogue_manager.user_name}:{dialogue_manager.entity_summary}",
    #                                                                         entity=f"{dialogue_manager.user_name}",
    #                                                                         input=dialogue_manager.chat_history)
    #     await generator.async_sync_call_streaming(prompt_entity, callback=callback_entity_summary)
    #     # await generator.async_sync_call_streaming(prompt_summary, callback=callback_summary)
    # if "情境更新" in task:
    #     # 情境模拟
    #     prompt_simulation = prompt.AGENT_SITUATION.format(dialogue_situation=dialogue_manager.situation,
    #                                                        dialogue_excerpt=dialogue_manager.chat_history,
    #                                                        user=dialogue_manager.user_name,
    #                                                        char=dialogue_manager.char_name)
    #     await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)
    # if "情绪更新" in task:
    #     # 情绪
    #     prompt_emotion = prompt.AGENT_EMOTION.format(emotion=char_info.emotional_state,
    #                                                  dialogue_situation=dialogue_manager.situation,
    #                                                  history=dialogue_manager.chat_history,
    #                                                  char=char_info.name)
    #     await generator.async_sync_call_streaming(prompt_emotion, callback=callback_emotion)


async def typewriter(content):
    head_idx = 0
    full_text = ""  # 用于累积所有打印的文本
    for resp in content:
        paragraph = resp.output['text']
        # 确保按字符而非字节打印
        for char in paragraph[head_idx:]:
            # 打印蓝色字体
            print("\033[34m{}\033[0m".format(char), end='', flush=True)
            full_text += char  # 添加字符到完整文本
            # 每个字符打印后暂停0.1秒
            # time.sleep(0.01)
        head_idx = len(paragraph)
        # 如果段落以换行符结束，保留该位置
        if paragraph.endswith('\n'):
            head_idx -= 1

    return full_text


async def callback_simulation(content):
    dialogue_manager.situation = content
    # await typewriter(content)
    # print(f"{GREEN}\n📏>情境模拟>>>>>{content}{RESET}")


async def callback_analysis(content):
    await typewriter(content)
    # print(f"{GREEN}\n📏>对话分析>>>>>{content}{RESET}")


async def callback_emotion(content):
    # char_emotion = content
    char_info.emotional_state = await typewriter(content)

    char_info = f"[兴趣:阅读童话书], [性格:内向，害羞], {char_info.emotional_state}，[生理状态:正常],[位置：客厅]，[动作：站立]"


async def callback_summary(content):
    # global summary
    # summary = content

    # entity_db.add_texts(content)
    # decoded_content = content.decode('utf-8')
    # await typewriter(decoded_content)
    # dialogue_manager.summary_history.append(decoded_content)
    print(f'{GREEN}\n📏>对话概要>>>>>decoded_content{RESET}')
    # print(f"{GREEN}\n📏>对话概要>>>>>{content}{RESET}")


async def callback_entity_summary(content):
    dialogue_manager.entity_summary = content
    print(f"{GREEN}\n📏>实体更新>>>>>{dialogue_manager.entity_summary}{RESET}")
    await typewriter(content)
    # print(f"{GREEN}\n📏>实体识别>>>>>{entity_user_summary}{RESET}")


@graphsignal.trace_function
# 决策模型
async def decision_agent(prompt_decision):
    await generator.async_sync_call_streaming(prompt_decision, callback=callback_chat)


#
# async def async_sync_call_streaming(prompt_simulation):
#     # 这里假设 generator.sample_sync_call_streaming 可以直接作为异步调用
#     # 如果不是，你可能需要在这个函数中使用其他的异步途径来调用它
#     await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)


print(f"{GREEN}\n📏>当前情境>>>>>{dialogue_manager.situation}{RESET}")
print(f"{GREEN}\n📏>事件>>>>><事件>猪鳄变出了金币，哥哥和兔叽得到一些金币，但猪鳄限制了数量。{RESET}")

from langchain_community.llms.tongyi import generate_with_retry

# import spacy
# nlp = spacy.load('zh_core_web_sm')
# 添加自定义词汇
# nlp.tokenizer.pkuseg_update_user_dict(["兔叽","哥哥"])
# 执行一些简单的NLP任务
# doc = nlp("卧室厨房乔布斯")
# for ent in doc.ents:
#     # 实体文本，开始位置，结束位置，实体标签
#     print(ent.text, ent.start_char, ent.end_char, ent.label_)
from pydantic import BaseModel


class GenerationRequest(BaseModel):
    data: str  # 数据模型


from fastapi.responses import StreamingResponse
import httpx
from sse_starlette.sse import EventSourceResponse
import requests
# @app.post("/stream-input")
# async def stream_input(request: Request):
#     # 这里是处理接收到的流式数据的逻辑
#     # 例如，将数据存储在队列中
#     pass
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"],  # 允许的头
)


@app.post("/generate/")
async def generate(request: GenerationRequest):
    global query
    query = request.data
    print(query)
    search_help_prompt = search_graph_helper.format(schema="", content=query)
    # intention_prompt = f"{prompt.INTENTION.format(chat_history=dialogue_manager.chat_history,input=query)}"
    # gpu_server_generator.generate_normal(intention_prompt, callback=callback_intention)
    llm = Tongyi(model_name="qwen-max-1201", top_p=0.1, dashscope_api_key="sk-dc356b8ca42c41788717c007f49e134a")
    params = {
        **{"model": llm.model_name},
        **{"top_p": llm.top_p},
    }
    completion = generate_with_retry(llm=llm, prompt=search_help_prompt, **params)
    print(completion)
    dialogue_manager.intention = completion["output"]["text"]
    dialogue_manager.intent_history.append(f'问：{query}')
    docs = vectordb.similarity_search_with_score(query)

    page_contents = []
    for doc, score in docs:
        # 将每个文档的内容和它的得分添加到page_contents列表
        if score < 0.4:
            page_contents.append(f"{doc.page_content} (余弦相似度: {score})")

    if len(page_contents):
        combined_contents = '\n'.join(page_contents)
        print(f"{ORANGE}📑>参考资料>>>>>\n{combined_contents}{RESET}")
        # reference = combined_contents

        # # 参考资料实体概括
        # rag_summary = prompt.AGENT_RAG_ENTITY.format(reference=combined_contents)  # 暂时不概括
        # gpu_server_generator.generate_normal(rag_summary, callback=callback_rag_summary)  # 暂时不概括

    else:
        combined_contents = "***没有合适的参考资料，需更加注意回答时的事实依据！避免幻觉！***"
    # # 决策模型
    # prompt_decision = prompt.AGENT_DECISION.format(user_profile=user_info,
    #                                                dialogue_situation=dialogue_situation,
    #                                                extracted_triplets=dialogue_manager.extracted_triplets,
    #                                                chat_history=dialogue_manager.chat_history,
    #                                                user=user_info.name, char=char_info.name, input=query)
    prompt_knowledge = prompt.KNOWLEDGE_GRAPH.format(text=prompt_test)
    # char_info = ("[兴趣:阅读童话书], [性格:内向，害羞], [情绪状态:生气"
    #              "   ]，[生理状态:饥饿],[位置：客厅]，[动作：站立]...")
    print(f"{GREEN}🎮>GameData(sample)>>>>>:{char_info}{RESET}")
    print(f"{GREEN}🎮>GameData(sample)>>>>>:{user_info}{RESET}")
    prompt_game = prompt.AGENT_ROLE_TEST.format(user=user_info.name, user_info=user_info,
                                                char=char_info.name, char_info=char_info,
                                                input=query, dialogue_situation=dialogue_manager.situation,
                                                user_entity=dialogue_manager.entity_summary,
                                                reference=combined_contents,
                                                lines_history=dialogue_manager.chat_history,
                                                summary_history=dialogue_manager.summary_history)
    print(dialogue_manager.chat_history)
    tasks = [
        update_emotion(),
        update_summary(),
        update_entity(),
    ]
    await asyncio.gather(*tasks)
    # 创建一个新的任务来运行 update_situation，传递回调函数
    asyncio.create_task(update_situation(on_update_situation_complete))
    return EventSourceResponse(generator.async_sync_call_streaming(prompt_game, callback=callback_chat))
