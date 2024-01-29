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

from langchain_community.graphs.graph_document import GraphDocument
from langchain_community.graphs.graph_document import Node, Relationship
from langchain_core.documents import Document
NEO4J_URI="neo4j+s://159d31d7.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="bKOuLr5ZGAGjFC-VMm1wonVhk1f3konW9OAEh0g8J-A"
AURA_INSTANCEID="159d31d7"
AURA_INSTANCENAME="Instance01"

from langchain.graphs import Neo4jGraph

# print(re)
def task_completed_notification():
    print("----------------------数据存储任务完成----------------------")
    data_get()


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
    output_file_path = '/simpleaichat/extracted_data.json'
    extract_and_save_as_json(llm_output, output_file_path, callback=task_completed_notification)


graphdb = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

npcName= "红心皇后"

query = f"""
MATCH (n)-[r]->(m)
WHERE n.npcName = '{npcName}'
RETURN n, r, m
LIMIT 10
"""
document_source = Document(
    page_content="动态游戏信息",
    metadata={"author": "leozy", "date": "2024"}
)
result = graphdb.query(query)
user = Node(id="1", type="user", properties={"name": "大头"})
charactor = Node(id="2", type="charactor", properties={"name": "兔叽"})
friendship = Relationship(source=user, target=charactor, type="FRIENDS_WITH", properties={"since": "2024"})
graph_doc = GraphDocument(nodes=[user, charactor], relationships=[friendship], source=document_source)
graphdb.add_graph_documents([graph_doc])


print(result)
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
# csvloader.file_path = "世界设定.csv"
# vectordb.add_documents(csvloader.load())

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
char_name = "兔叽"
intention = ""
entity_user = user_name
entity_char = char_name
entity_user_summary = ""
entity_char_summary = ""
user_info = "[兴趣:阅读], [性格:内向], [近期情感:正常]"
char_emotion = "[情绪状态:正常]"
char_info = f"[兴趣:阅读童话书], [性格:内向，害羞], {char_emotion}，[生理状态:正常],[位置：客厅]，[动作：站立]"

summary = ""
summary_history= ""

user_profile = "[兴趣:阅读], [性格:内向], [近期情感:正常]"
extracted_triplets = [("用户", "无明确需求")]
dialogue_situation = """
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

chat_content = ""
# ANSI转义序列
ORANGE = '\033[33m'
GREEN = '\033[32m'
RESET = '\033[0m'

entity_db = Chroma.from_documents(documents=documents_people, embedding=embedding_model)
dialogue_situation = dialogue_situation.format(char=char_name, user=user_name)

# 意图识别回调
def callback_intention(content, usage):
    # print(f"{ORANGE}🔷🔷🔷生成文本🔷🔷🔷\n{text}{RESET}")
    global intention
    intention = content
    # print(f"{GREEN}\n📏>辅助意图>>>>>{content}{RESET}")



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
    task = ""
    head_idx = 0
    print(f"{GREEN}\n📑>Chain of thought>>>>>:{RESET}")
    print(f"{GREEN}🎮>GameData(sample)>>>>>:{char_info}{RESET}")
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
        answer_parts = parts[1].split("TASK")
        # if answer_parts:
        chat_content = f"{char_name}{parts[1].strip()}"

        impression_part = chat_content.split("\n")
        if len(impression_part) > 1:
            task = impression_part[1].strip()
            print(f"{GREEN}\n📏>TASK>>>>>{task}{RESET}")

            # cleaned_text = re.sub(r'[^a-zA-Z]', '', answer_parts[1].strip())
    # print(f"{GREEN}\n⛓FINAL>>>>>>{chat_content}{RESET}")
    chat_history.append(f'{user_name}：{query}')
    chat_history.append(chat_content)
    intent_history.append(chat_content)
    if "记忆更新" in task:
        # 概要提示
        prompt_summary = prompt.DEFAULT_SUMMARIZER_TEMPLATE.format(new_lines=chat_history, summary=summary,
                                                                   user=user_name, char=char_name)
        # 实体识别
        prompt_entity = prompt.DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE.format(history=chat_history,
                                                                            summary=f"{entity_user}:{entity_user_summary}",
                                                                            entity=f"{entity_user}",
                                                                            input=chat_history)
        await generator.async_sync_call_streaming(prompt_entity, callback=callback_entity_summary)
        # await generator.async_sync_call_streaming(prompt_summary, callback=callback_summary)
    if "情境更新" in task:
        # 情境模拟
        prompt_simulation = prompt.AGENT_SIMULATION.format(dialogue_situation=dialogue_situation,
                                                           dialogue_excerpt=chat_history,
                                                           user=user_name, char=char_name)
        await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)
    if "情绪更新" in task:
        # 情绪
        prompt_emotion = prompt.AGENT_EMOTION.format(emotion=char_emotion,
                                                     dialogue_situation=dialogue_situation,
                                                     history=chat_history,
                                                     char=char_name)
        await generator.async_sync_call_streaming(prompt_emotion, callback=callback_emotion)
async def typewriter(content):
    head_idx = 0
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
    return paragraph
async def callback_simulation(content):
    global dialogue_situation
    dialogue_situation = content
    # await typewriter(content)
    # print(f"{GREEN}\n📏>情境模拟>>>>>{content}{RESET}")

async def callback_analysis(content):
    await typewriter(content)
    # print(f"{GREEN}\n📏>对话分析>>>>>{content}{RESET}")

async def callback_emotion(content):
    global char_emotion
    global char_info
    # char_emotion = content
    char_emotion=  await typewriter(content)

    char_info = f"[兴趣:阅读童话书], [性格:内向，害羞], {char_emotion}，[生理状态:正常],[位置：客厅]，[动作：站立]"
async def callback_summary(content):
    global summary
    summary = content
    await typewriter(content)
    entity_db.add_texts(content)
    # print(f"{GREEN}\n📏>对话概要>>>>>{content}{RESET}")

async def callback_entity_summary(content):
    global entity_user_summary
    entity_user_summary = content
    print(f"{GREEN}\n📏>实体更新>>>>>{entity_user_summary}{RESET}")
    await typewriter(content)
    # print(f"{GREEN}\n📏>实体识别>>>>>{entity_user_summary}{RESET}")

@graphsignal.trace_function
#决策模型
async def decision_agent(prompt_decision):
    await generator.async_sync_call_streaming(prompt_decision, callback=callback_chat)


async def async_sync_call_streaming(prompt_simulation):
    # 这里假设 generator.sample_sync_call_streaming 可以直接作为异步调用
    # 如果不是，你可能需要在这个函数中使用其他的异步途径来调用它
    await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)
print(f"{GREEN}\n📏>当前情境>>>>>{dialogue_situation}{RESET}")
print(f"{GREEN}\n📏>事件>>>>><事件>猪鳄变出了金币，哥哥和兔叽得到一些金币，但猪鳄限制了数量。{RESET}")



while True:
    # 输入

    query = input("\n输入: ")
    # 意图识别
    intention_prompt = f"{prompt.INTENTION}\n 问:{intent_history}{query}\n预期输出:"
    gpu_server_generator.generate_normal(intention_prompt, callback=callback_intention)
    intent_history.append(f'问：{query}')
    docs = vectordb.similarity_search_with_score(intention)
    entity_doc = entity_db.similarity_search_with_score(user_name)
    entity_contents = []
    for doc, score in entity_doc:
        # 将每个文档的内容和它的得分添加到page_contents列表
        if score < 0.3:
            entity_contents.append(f"{doc.page_content} (得分: {score})")
            print(f"{GREEN}\n📑>实体识别>>>>>{doc.page_content}{RESET}")


    # 对话情感检索
    # 对话主题检索
    # 对话特征检索

    # 直接检索

    page_contents = []
    for doc, score in docs:
        # 将每个文档的内容和它的得分添加到page_contents列表
        if score < 0.35:
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
        # print(f"{ORANGE}📑❌>参考资料>>>>>未识别到有效资料，需更加注意回答时的事实依据！避免幻觉！***{RESET}")




    # 生成
    # try:
    #     # final_prompt = f"{prompt.COSER}\n {prompt.RAG}\n参考资料:\n{combined_contents}\n历史记录：{chat_history}\n{prompt.AGENT_REACT}\n{prompt.REACT_FEW_SHOT}\n开始\nuser:{query}\n兔叽:"
    #     # final_prompt = prompt.AGENT_REACT.format(impression= impression,history2=chat_history, reference=combined_contents, input=query,user=user_name,char=char_name)
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
    #     #     topic_prompt = prompt.TOPIC.format(history2=topic_history, topic_or_activity=topic_or_activity,
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
        global char_info
        global user_info
        # # 概要提示
        # prompt_summary = prompt.DEFAULT_SUMMARIZER_TEMPLATE.format(new_lines=chat_history, summary=summary, user=user_name, char=char_name)
        # # 实体识别
        # prompt_entity = prompt.DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE.format(history2=chat_history,
        #                                                                     summary=entity_user_summary, entity_user=entity_user,
        #                                                                     input=chat_history)
        # # 情境模拟
        # prompt_simulation = prompt.AGENT_SIMULATION.format(dialogue_situation=dialogue_situation, dialogue_excerpt=chat_history,
        #                                                    user=user_name, char=char_name)
        # 决策模型
        prompt_decision = prompt.AGENT_DECISION.format(user_profile=user_profile,
                                                       dialogue_situation=dialogue_situation,
                                                       extracted_triplets=extracted_triplets,
                                                       chat_history=chat_history,
                                                       user=user_name, char=char_name, input=query)

        # prompt_analysis = prompt.AGENT_ANALYSIS.format(history2=chat_history,user= user_name,char=char_name,input=query,reference=combined_contents)

        # char_info = ("[兴趣:阅读童话书], [性格:内向，害羞], [情绪状态:生气"
        #              "   ]，[生理状态:饥饿],[位置：客厅]，[动作：站立]...")
        prompt_game = prompt.AGENT_ROLE_TEST.format(user=user_name,user_info=user_info,
                                                    char=char_name,char_info=char_info,
                                                    input=query,dialogue_situation=dialogue_situation,
                                                    reference=combined_contents,lines_history=chat_history,summary_history=summary)
        # await generator.async_sync_call_streaming(prompt_analysis, callback=callback_analysis)
        await generator.async_sync_call_streaming(prompt_game, callback=callback_chat)
        # char_info = "[兴趣:阅读童话书], [性格:内向，害羞], [情绪状态:好奇]，[生理状态:正常],[位置：厨房]，[动作：站立]"
        # prompt_game = prompt.AGENT_ROLE.format(user=user_name, user_info=user_info, char=char_name, char_info=char_info,
        #                                        input=query, dialogue_situation=dialogue_situation,
        #                                        reference=combined_contents, history2=chat_history)
        # await generator.async_sync_call_streaming(prompt_game, callback=callback_chat)
        # await generator.async_sync_call_streaming(prompt_entity, callback=callback_entity_summary)
        # await generator.async_sync_call_streaming(prompt_summary, callback=callback_summary)
        # await generator.async_sync_call_streaming(prompt_simulation, callback=callback_simulation)
        # await generator.async_sync_call_streaming(prompt_decision, callback=callback_chat)


    # 运行主函数
    asyncio.run(main())


