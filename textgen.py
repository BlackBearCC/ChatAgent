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
import re  # 导入 re 模块
NEO4J_URI = "neo4j+s://159d31d7.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "bKOuLr5ZGAGjFC-VMm1wonVhk1f3konW9OAEh0g8J-A"
AURA_INSTANCEID = "159d31d7"
AURA_INSTANCENAME = "Instance01"

from langchain.graphs import Neo4jGraph
import json


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
summary_history = ""

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

prompt_test = """
关键地点：博物馆
关键人物：咕噜、呱呱
故事概要：咕噜和呱呱是博物馆的保安，他们的职责是维持博物馆的秩序，但由于天生的生理构造咕噜的眼睛只能往两边看，所以经常用余光瞥人，而呱呱的眼睛只能往头顶看，他努力往前看的时候总给人一种蔑视感；所以大家都觉得他们目中无人，很难相处。当然他们彼此之间由于无法对视，也并不认同对方。久而久之他们开始接受自己的人设，不再刻意解释。{user}和{char}不知道写个什么故事，想来到博物馆找一些灵感，遇到了博物馆盗窃案和咕噜和呱呱的重重阻挠，{char}决定写一个推理故事，自己成为大侦探，破案的同时解开了他俩的心结，发现他俩和好比抓到犯人更有意义，觉得自己不想继续当一个合格的侦探，开始想别的故事。
一
（地点：博物馆前门）
”你好，鱼鱼先生~请问我们可以进去吗？~“{char}可爱又有礼貌的询问了一下。
”我叫咕噜，请。“咕噜面朝前方，但仿佛并没有看到{char}。
”等等！很抱歉您不能进去。“咕噜突然往后一步拦住了{char}，“您的着装不规范。”
“啊？可是你刚刚还说...”{char}不开心的嘟嘟嘴。
“抱歉，我只有在侧面才能看清您。”咕噜仿佛在机械的背台词。
“呜呜，可是我只有这一件衣服嘛...”{char}可怜巴巴的看着咕噜，但咕噜仿佛并没有看到{char}。
“你这么想去博物馆看看的话，不如我们去侧门试试吧~“{user}小声建议道。
”好！“{char}又重新打起了精神。
（地点：博物馆侧门）
“侧门是呱呱先生！它好像只能看到天花板！”{char}兴奋的说道。
“可是天花板是镜面做的呢。”{user}回答。
“或许，我们可以..."{char}转动着小眼睛，仿佛想到了什么好主意，躲进了{user}的大衣里。
“你好，我想进入博物馆参观。”{user}礼貌的说道。
“请，呱。“呱呱面无表情的说道。
”阿——“{char}小声的打了个喷嚏。
”阿嚏——“{user}赶紧接上了喷嚏，呱呱看了一眼天花板镜子里的{user}，并没有说什么。
/n
（地点：博物馆大厅）
”成功过关！“{char}从{user}的大衣里跳了出来，一脸得意的模样。
”不过，我这么做不会给咕噜和呱呱带来麻烦吧？他们好像对待工作很严肃的样子..."{char}苦恼的看向{user}。
“你要是不捣蛋应该没问题吧。”{user}话音刚落，博物馆的灯瞬间灭了，警报立刻响了起来。
“啊啊啊！不会是来抓我们的吧！”{char}赶紧又躲进了{user}的大衣里。
（博物馆的灯随即又恢复了供电）
“感觉不是很妙的样子..."{user}看着从正门冲进来的咕噜，正好用侧面死死的盯着他俩，且迅速转身向他俩冲了过来。
”我已经看到你的小尾巴了！是谁放你们进来的？！“咕噜突然在十步开外刹住了脚步，努力张大了嘴字正腔圆的质问道，“就是你们偷了博物馆的镇馆之宝吗？”
”啊！我们可没有偷东西呢！“{char}偷偷探出了半个小脑袋，着急的解释道。
”应该是有什么误会吧，博物馆是失窃了吗？“{user}礼貌的问道。
”对不起，请你们配合检查。”咕噜在十步开外严肃的叫道。
“他们，我放进来的。”呱呱慢悠悠的走了过来，漫不经心的说道。
“ 所以这就是你一个人看门的目的？！把不法分子放进来破坏博物馆？！”咕噜突然从刚刚的严肃变得激动起来。
“咕噜，喝水。”呱呱慢悠悠的说道，之间咕噜拿起手边的保温杯，喝了一口后便平静了下来。
“先找到馆宝吧。”呱呱看了一眼{user}和{char}，“小家伙藏得挺好，先接受一下检查吧。”
“对...对不起咕噜先生，偷偷溜进来是我不对。”{char}老老实实的站了出来，认真的道歉。
“啊，那个，下次不许这样了啊。”咕噜揣着保温杯突然有点脸红，语气也不自在起来。
"原来咕噜也没有这么凶巴巴嘛~“{char}偷偷跟{user}说。
“你们有看到什么异常情况吗？”呱呱问道。
”我们刚进来，还没来得及...“{user}话还没说完，{char}就赶紧拉住了{user}
”不如我们就写一个大侦探的故事吧！我想当大侦探！哥哥！“{char}兴奋的小声跟{user}说道。
”不过，我想我们可以协助调查，为你们提供更多的信息。“{user}清了清嗓子，认真的说道。
”博物馆现在确实需要帮助，那就拜托你们了。“呱呱悠悠的说道。
”这么关键的时候！你是不是又想偷懒！“咕噜突然又激动起来。
”多个帮手能早点找到馆宝，是好事。“，呱呱说道，”博物馆的馆宝是一颗稀有的矿石，刚才自动触发的警报就是因为它消失了。“
”那我们快去现场调查吧！“{char}挥舞着小手，干劲十足。
“那我们分头行动，我和呱呱先去调查一下博物馆的录像，你和咕噜去现场收集线索好吗？”{user}问{char}
“好哒，咕噜先生出发！”{char}蹦蹦跳跳的跑向咕噜，咕噜有些不知所措的跟在{char}身后。
/n
（地点：录像室）
”从录像带上看，离展柜最近的只有咕咕，但毛儿手脚灵活的很，不过他们都是博物馆的老熟人了，我并不怀疑他们。"呱呱慢悠悠的说道，“虽说我从没见过你们，你们一出现就出事了，但我也不怀疑你们。”
“？我不是很明白...”{user}回答道。
“直觉吧，好了，说说你的发现吧。"呱呱把画面转向{user}。
（打开录像带，在断电前后的画面上圈出可疑的点）
{user}：”咕咕小姐前后几乎没有移动过位置，连表情都很连贯，看上去像是吓坏了。“
  ”毛儿有臂长的优势，但很难如此精巧的取到矿石...“
  ”我猜测是一种个头远小于他们的家伙干的，当然还有一种可能，那就是矿石自己跑了..."
"哦？矿石自己跑了，听上去是个值得调查的方向哈哈哈。”呱呱开心的大笑道，“那我们去看看你的小伙伴有没有找到什么它自己跑了的线索。”
/n
（地点：博物馆中心区域）
“哥哥！哥哥你快来看！”{char}看到{user}，兴奋的蹦跳着叫道，“我发现矿石自己逃跑的线索了！“
”你！你们简直就是胡闹！“咕噜皱紧了眉头，紧紧的攥着保温杯。
”矿石本来就是镇子上的天外来物，现在自己跑了也很合理嘛~“呱呱笑着拍了拍咕噜的肩膀。
”我在陈列台旁边薄薄的灰上找到了矿石的小脚印！咕噜给我看过矿石的模样，每个印记都能和矿石的棱角对上！“ {char}认真的凑在台子前指着淡淡的痕迹说道。
”也有可能是某种飞行动物拖动矿石留下的痕迹！“咕噜喝了一口水，冷漠的说道。
”嗯，咕噜说的也很有道理呢！“{char}认真的点了点头。
”噗...那个，我就是随便猜测的。“咕噜一口水差点喷出来，完全没想到{char}会认同自己。
”对了，矿石是天外来物嘛？“{user}转向呱呱问道。
”是咕噜在森林里发现的，我们从没见过这样的矿石，而且它好像还砸出了一个大洞。“呱呱说道。
”他还打算在那个洞里种菜，太离谱了！！“咕噜一想起这事又激动起来。
"哈哈，哈哈，你不是前阵子叨叨着想吃嫩白菜。”呱呱憨憨的笑了起来。
“哇！我也喜欢吃嫩白菜！我也可以帮呱呱种菜！”{char}一脸馋样的举起了小手。
“不如我们现在就去那个洞附近看看吧~”{user}提议道。
“好耶！我要去看看我的白菜天堂！”{char}迫不及待地就要往外跑。
/n
（森林怪洞附近）
"哇，这个洞好大啊！" {char}惊奇地张大了眼睛，兴奋地绕着洞口转了一圈。
“确实，我发现这个洞的时候也吓了一跳。”咕噜喝了口水，瘪着嘴生气的回忆道，“那天原本是过来散心的，结果还掉进了洞里。”
“这个洞看着不像是一个普通的坑洞，咕噜先生，你当时是怎么发现矿石的？”{user}好奇地询问。
“说起来挺巧，我一脚踩空滑下去那会儿把表层的土块震了下来“，咕噜有点怀疑，”矿石正好就在我右侧方露了出来，好像就在那儿等着我似的。”
“说不定它还能真自己跑呢~”呱呱乐呵呵的补充道。
（观察洞口，寻找奇怪的地方）
“看这边，有些奇怪的痕迹。”{user}指着洞口旁的一些痕迹说道。
“发现这些脚印异常细小，且呈现出一种非常规的排列。”{user}说道，“这不像是普通动物留下的……难道是……”
“我觉得这可能是矿石自己留下的。”{char}兴奋地说。
“看来这矿石还真是自己回家了，我们去洞里看看。”呱呱推测道。
“看来你们是认定了这矿石自己能长腿了！”咕噜翻了翻白眼，无可奈何的跟在后面。
咕噜拿出手电筒，照进洞里，但只能看到一片漆黑。“真要进去里面？”他问道。
“当然！”{char}毫不犹豫地答道，迫不及待就要往里走。
/n
（怪洞深处）
“前面好像有亮光！”{char}激动的轻声说道。
“侧面的石壁好像会透出隐约的光亮，都在向同个方向延伸。”咕噜仔细观察着周围说道。
“有东西在动！”{char}小声说道。
“大家小心，我们一起过去看看。”{user}说道。
大家小心地靠近声音的来源，只见在一个角落里，那颗失窃的矿石正闪烁着光芒，周围有一些小型的生物正在围绕着它。这些生物看起来像是小型机器人，却有着生物般的动作。
（发现了矿石和一些小型的不明生物）
“你看，矿石！“呱呱一脸早就知道的表情看着咕噜。
”没想到矿石居然真的在这里。“咕噜小声嘟囔着。
“哇，这些小东西是什么？”{user}惊讶地问。
“看起来像是一些机器生物。看来就是他们运走了矿石。”{user}说道。
“我就说矿石不会自己长脚嘛！”咕噜补充道。
（{char}小心翼翼地走近那些生物，它们并没有攻击的意图，只是好奇地看着陌生的来客。）
”哇，他们是外星小可爱！“{char}开心的观察着这些生物，”他们身上有和矿石一样的光亮！“
“看来，这次的盗窃案是个误会。”{char}悄悄地对{user}说，“这些小生物可能是想把矿石带回家。”
“或许矿石留在这里才是更适合的，你们觉得呢？”{user}问。
“我想我们可以和博物馆商量，把矿石的展位改为这个洞穴。”呱呱提议。
“还可以保护这个洞穴，让这些生物安全地生活在这里，我同意！”咕噜点头。
“那我们就这么决定了！”{char}高兴地说。
”那我们先回博物馆报告这起事件了，感谢你们的协助！“咕噜一板一眼的说道。
”咕噜先生！我在博物馆看见呱呱偷偷给你装满了水！他是你很好的朋友哦！“{char}突然说道。
”咳，谁要跟他当很好的朋友..."咕噜极其不自然的喝了一口水。
“看来我一个人是看不住这门咯，还得跟你一起看才行。”呱呱用胳膊肘撞了撞咕噜，憨憨地笑着。
“早说了你不行了，赶紧回去吧你!”咕噜一脸不好意思的推着呱呱就往外走，“谢谢你们啦，以后常来博物馆玩！”
“很好，作为小侦探的第一步，我想你已经成功迈出了。“{user}摸了摸{char}的头。
”嘘，哥哥，有个秘密。“{char}看着两人远去的背影，拽着{user}的袖子小声地说，”矿石会说话。“
"""
prompt_test.format(char=char_name, user=user_name)
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
        return GraphDocument(nodes=list(nodes.values()), relationships=relationships, source=document_source)
    except json.JSONDecodeError as e:
        raise ValueError(f"解析 JSON 时出错：{e}")


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
    char_emotion = await typewriter(content)

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
# 决策模型
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

        prompt_knowledge = prompt.KNOWLEDGE_GRAPH.format(text=prompt_test)
        # char_info = ("[兴趣:阅读童话书], [性格:内向，害羞], [情绪状态:生气"
        #              "   ]，[生理状态:饥饿],[位置：客厅]，[动作：站立]...")
        prompt_game = prompt.AGENT_ROLE_TEST.format(user=user_name, user_info=user_info,
                                                    char=char_name, char_info=char_info,
                                                    input=query, dialogue_situation=dialogue_situation,
                                                    reference=combined_contents, lines_history=chat_history,
                                                    summary_history=summary)
        # await generator.async_sync_call_streaming(prompt_analysis, callback=callback_analysis)
        await generator.async_sync_call_streaming(prompt_knowledge, callback=callback_knowledge_graph)

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
