"""FastAPI 主入口模块"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("✅ 数据库初始化完成")
    try:
        from app.rag.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        await kb.initialize_default_knowledge()
        logger.info("✅ 知识库初始化完成")
    except Exception as e:
        logger.warning(f"⚠️ 知识库初始化失败: {e}")
    yield
    logger.info("👋 应用关闭")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
              description="搬家/装修规划 AI Agent 系统", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.agent import router as agent_router
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(agent_router)

@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/info")
async def api_info():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "llm_provider": settings.LLM_PROVIDER}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
