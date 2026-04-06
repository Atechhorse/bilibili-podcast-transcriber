"""
LLM 客户端
"""
from typing import Dict
import requests
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMClient:
    """LLM 客户端，用于说话人身份推理"""
    
    def __init__(self, llm_config: Dict):
        self.provider = llm_config.get('provider', 'deepseek')
        self.model = llm_config.get('model', 'deepseek-chat')
        self.api_key = llm_config.get('api_key')
        self.base_url = llm_config.get('base_url', 'https://api.deepseek.com')
        
        if not self.api_key:
            logger.warning("未配置 LLM API Key，说话人身份推理将无法使用")
    
    def chat(self, prompt: str) -> str:
        """
        调用 LLM 进行对话
        
        Args:
            prompt: 提示词
            
        Returns:
            LLM 返回的文本
        """
        if not self.api_key:
            raise ValueError("未配置 LLM API Key")
        
        if self.provider == 'deepseek':
            return self._chat_deepseek(prompt)
        elif self.provider == 'openai':
            return self._chat_openai(prompt)
        else:
            raise ValueError(f"不支持的 LLM provider: {self.provider}")
    
    def _chat_deepseek(self, prompt: str) -> str:
        """调用 DeepSeek API"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise
    
    def _chat_openai(self, prompt: str) -> str:
        """调用 OpenAI API"""
        url = f"{self.base_url}/v1/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            raise