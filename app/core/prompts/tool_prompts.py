search_helper = """
我提供了一段对话文本,请按照以下步骤操作：
1. 识别并列出可用于图数据库查询的关键搜索词。这些应包括具体的实体名、事件名或特定概念。请提供一个简短的列表。
2. 确定并列出适用于向量检索的关键搜索词。这应包括对话的主题词、抽象概念或核心思想。请同样提供一个简短的列表。

请注意，这两类搜索词的选取应基于对话内容的深入理解和关键信息的提取，而不需要显示思维链的整个过程，另外这两个搜索词是允许重复的。

Example:
对话文本：“昨天我参加了在波士顿举行的科技创新会议，讨论了人工智能的未来趋势。”
GraphSearch：波士顿, 科技会议, AI。
VectorSearch：科技趋势, AI未来。

对话文本：“我最近读了一本关于第二次世界大战的历史书，特别是关于诺曼底登陆的部分。”
GraphSearch：第二次世界大战，诺曼底登陆，历史书。
VectorSearch：军事历史，重要事件，诺曼底登陆。
End of Example

START:
{content}
"""
search_graph_helper = """
Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:
# How many people played in Top Gun?
MATCH (m:Movie {{title:"Top Gun"}})<-[:ACTED_IN]-()
RETURN count(*) AS numberOfActors
请注意你生成的查询变量必须是中文。
The question is:
{content}
"""