class CallbackHandler:
    def handle(self, callback_type, content):
        if callback_type == 'chat':
            self._handle_chat(content)
        elif callback_type == 'knowledge_graph':
            self._handle_knowledge_graph(content)
        # 其他回调处理
        else:
            raise ValueError("Unsupported callback type")

    def _handle_chat(self, content):
        # 处理聊天回调的逻辑
        pass

    def _handle_knowledge_graph(self, content):
        # 处理知识图谱回调的逻辑
        pass