"""
LLM Service
===========
Handles text generation using Gemini API or OpenRouter API.
No local models — fully API-based for cloud deployment.
"""

import logging
import requests
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_text(prompt: str, system_instruction: Optional[str] = None) -> str:
    """
    Main entry point for text generation.
    Uses OpenRouter as the exclusive stable provider.
    """
    if not settings.use_llm:
        return ""

    try:
        return await _call_openrouter(prompt, system_instruction)
    except Exception as e:
        logger.error(f"OpenRouter failed: {e}")
        return "Generation failed. Please check your API keys or try again later."


import httpx

async def _call_gemini(prompt: str, system_instruction: Optional[str] = None) -> str:
    if not settings.gemini_api_key:
        raise ValueError("Gemini API key not configured")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
        }
    }
    if system_instruction:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    # Guard against blocked/empty responses
    candidates = data.get("candidates", [])
    if not candidates:
        reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
        raise ValueError(f"Gemini returned no candidates (blockReason: {reason})")

    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ValueError("Gemini response has empty content parts")

    return parts[0]["text"]


async def _call_openrouter(prompt: str, system_instruction: Optional[str] = None) -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OpenRouter API key not configured")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "google/gemini-2.0-flash-lite-001",  # Verified working via OpenRouter
        "messages": messages,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]
