from app.core.config import settings
import openai
from zhipuai import ZhipuAI
openai.api_key = settings.OPENAI_API_KEY
zhipu_client = ZhipuAI(api_key=settings.CHATGLM_API_KEY) if settings.CHATGLM_API_KEY else None
def get_ai_response(prompt: str) -> str:
    if settings.ACTIVE_MODEL == "chatglm3-6b" and zhipu_client:
        return zhipu_client.chat.completions.create(model="chatglm3-6b", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    return openai.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
