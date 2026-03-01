"""
LLM Service
===========
Handles text generation using local models, Gemini API, or OpenRouter API.
Implements failover logic as requested.
"""

import logging
import requests
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded local model
_local_pipeline = None

def _get_local_pipeline():
    global _local_pipeline
    if _local_pipeline is None:
        try:
            from transformers import pipeline
            logger.info("Loading local LLM model: %s", settings.llm_model)
            _local_pipeline = pipeline("text2text-generation", model=settings.llm_model)
        except Exception as e:
            logger.error("Failed to load local model: %s", e)
    return _local_pipeline

async def generate_text(prompt: str, system_instruction: Optional[str] = None) -> str:
    """
    Main entry point for text generation.
    Supports failproof switching between providers.
    """
    if not settings.use_llm:
        return ""

    providers = []
    if settings.llm_provider == "gemini":
        providers = ["gemini", "openrouter", "local"]
    elif settings.llm_provider == "openrouter":
        providers = ["openrouter", "gemini", "local"]
    else:
        providers = ["local"]

    if not settings.failproof_llm:
        providers = [settings.llm_provider]

    for provider in providers:
        try:
            if provider == "gemini":
                return await _call_gemini(prompt, system_instruction)
            elif provider == "openrouter":
                return await _call_openrouter(prompt, system_instruction)
            elif provider == "local":
                return await _call_local(prompt)
        except Exception as e:
            logger.warning(f"LLM Provider {provider} failed: {e}. Switching to next...")
            continue
    
    logger.error("All LLM providers failed.")
    return "Generation failed. Please try again later or check your API keys."

async def _call_gemini(prompt: str, system_instruction: Optional[str] = None) -> str:
    if not settings.gemini_api_key:
        raise ValueError("Gemini API key not configured")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    if system_instruction:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    return data['candidates'][0]['content']['parts'][0]['text']

async def _call_openrouter(prompt: str, system_instruction: Optional[str] = None) -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OpenRouter API key not configured")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "anthropic/claude-3.5-sonnet", # High quality default for OpenRouter
        "messages": messages
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    return data['choices'][0]['message']['content']

async def _call_local(prompt: str) -> str:
    pipe = _get_local_pipeline()
    if pipe:
        # Local model (flan-t5) is limited, but works offline
        result = pipe(prompt, max_length=512, truncation=True)
        return result[0]['generated_text']
    raise RuntimeError("Local model not available")
