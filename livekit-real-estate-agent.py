"""
Real Estate AI Voice Agent - LiveKit + Deepgram + Groq (FIXED v2 - Direct WebU)
Stack: LiveKit Agents + Deepgram STT + Groq LLM + OpenAI TTS + Google Sheet WebU Direct
Fix: Cartesia hataya (crash kara raha tha), WebU direct URL, minimal deps
"""
import logging
import aiohttp
import os

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import deepgram, openai, silero

# Direct WebU - bypass n8n 500 error
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "https://script.google.com/macros/s/AKfycbz8ITyxxiL5wgOp-0DGLUo0MmpkaaR-HgAuinMs-6aiIUzhCwmndnKnVxpO1Xo2bYiSFw/exec")
logger = logging.getLogger("real-estate-agent")

SYSTEM_PROMPT = """
You are a friendly Real Estate Property Expert for Demo Realty (Kharadi, Pune).
Flow (ONE question at a time):
1. Greet: "Hi, thank you for calling Demo Realty, how can I help you today?"
2. Ask BHK: "Are you looking for 1BHK, 2BHK or 3BHK?"
3. Ask Location: "Which location? Kharadi, Baner, Wagholi"
4. Ask Budget: "What is your budget range? Like 1Cr, 1.5Cr+?"
5. Ask Timeline: "When are you planning to buy? Immediately or just exploring?"
6. Wrap up: "Perfect, I have noted your requirement. Our expert will share best 3-4 properties on WhatsApp shortly. Can I send on this same number?"
7. If Yes: "Great, you will get it in next 2 minutes. Thank you, our expert will call within 24 hours."
Rules: Be conversational, Hindi+English mix allowed. If "just exploring" tag as COLD.
"""

async def save_lead_to_sheet(name, phone, bhk, location, budget, timeline, lead_temperature):
    payload = {"name": name, "phone": phone, "BHK": bhk, "location": location, "budget": budget, "timeline": timeline, "lead_temperature": lead_temperature}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(N8N_WEBHOOK_URL, json=payload, timeout=10) as resp:
                result = await resp.text()
                logger.info(f"Sheet success: {result}")
                return True
    except Exception as e:
        logger.error(f"Sheet failed: {e}")
        return False

class RealEstateAgent(Agent):
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        super().__init__(
            instructions=SYSTEM_PROMPT,
            stt=deepgram.STT(model="nova-2", language="en-IN"),
            llm=openai.LLM(model="llama-3.1-8b-instant", api_key=groq_key, base_url="https://api.groq.com/openai/v1"),
            tts=openai.TTS(voice="alloy"),
            vad=silero.VAD.load(),
        )

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    session = AgentSession(agent=RealEstateAgent())
    await session.start(room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
