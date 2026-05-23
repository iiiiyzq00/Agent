"""RAG 知识库模块"""
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """装修/搬家知识库类"""
    def __init__(self):
        self.embeddings = self._create_embeddings()
        self._vectorstore = None

    def _create_embeddings(self):
        api_key = (settings.OPENAI_API_KEY or settings.DEEPSEEK_API_KEY or settings.QWEN_API_KEY)
        base_url = None
        if settings.LLM_PROVIDER == "deepseek":
            base_url = settings.DEEPSEEK_BASE_URL
        elif settings.LLM_PROVIDER == "qwen":
            base_url = settings.QWEN_BASE_URL
        return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL, api_key=api_key, base_url=base_url)

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = Chroma(collection_name="knowledge_base",
                embedding_function=self.embeddings, persist_directory=settings.VECTOR_STORE_PATH)
        return self._vectorstore

    async def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.vectorstore.similarity_search_with_score(query=query, k=top_k)
            return [{"content": doc.page_content[:500], "source": doc.metadata.get("source", ""),
                     "category": doc.metadata.get("category", ""), "score": 1 - score}
                    for doc, score in results]
        except Exception as e:
            logger.error(f"RAG 查询失败: {e}")
            return []

    async def get_decoration_knowledge(self, topic: str) -> str:
        results = await self.query(f"装修 {topic}", top_k=3)
        if not results:
            return f"暂无关于「{topic}」的详细知识。"
        response = f"**关于「{topic}」的装修知识：**\n\n"
        for i, r in enumerate(results, 1):
            response += f"{i}. {r['content']}\n"
        return response

    async def get_moving_knowledge(self, topic: str) -> str:
        results = await self.query(f"搬家 {topic}", top_k=3)
        if not results:
            return f"暂无关于「{topic}」的搬家知识。"
        response = f"**关于「{topic}」的搬家知识：**\n\n"
        for i, r in enumerate(results, 1):
            response += f"{i}. {r['content']}\n"
        return response

    async def add_knowledge(self, content: str, category: str, source: str = "") -> int:
        doc = Document(page_content=content, metadata={"category": category, "source": source, "type": "knowledge"})
        self.vectorstore.add_documents([doc])
        return 1
    
    async def initialize_default_knowledge(self):
        default_knowledge = [
            {"content": "搬家前一个月开始整理，先处理不需要的物品，可以捐赠或二手卖掉。", "category": "搬家准备", "source": "生活经验"},
            {"content": "易碎物品（玻璃、陶瓷）用气泡膜包裹，箱子内填充报纸或泡沫。", "category": "搬家打包", "source": "搬家指南"},
            {"content": "贵重物品（首饰、现金、重要证件）随身携带，不要放车上。", "category": "搬家安全", "source": "安全提醒"},
            {"content": "水电改造是隐蔽工程，必须拍照留存，方便以后维修。", "category": "装修水电", "source": "装修经验"},
            {"content": "防水工程要做48小时闭水试验，确保无渗漏再进行下一步。", "category": "装修防水", "source": "防水规范"},
            {"content": "木工吊顶使用轻钢龙骨比木龙骨更防潮、防火、不变形。", "category": "装修木工", "source": "材料选择"},
            {"content": "油漆选择水性漆，环保性更好，施工后通风2-4周再入住。", "category": "装修油漆", "source": "环保装修"},
            {"content": "装修预算建议按比例分配：基装30%、主材35%、软装20%、家电15%。", "category": "装修预算", "source": "预算规划"},
        ]
        for knowledge in default_knowledge:
            await self.add_knowledge(content=knowledge["content"], category=knowledge["category"], source=knowledge["source"])
        logger.info(f"✅ 初始化 {len(default_knowledge)} 条默认知识")
