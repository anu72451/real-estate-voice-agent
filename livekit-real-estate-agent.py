"""
Real Estate AI Voice Agent - LiveKit + Deepgram + Groq (FREE)
Stack: LiveKit Agents + Deepgram STT + Groq LLM + Cartesia TTS + Plivo SIP + n8n Webhook (Railway)
Updated for FREE Stack: No OpenAI key needed, uses Groq
"""
import asyncio
import logging
import aiohttp
import os

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import deepgram, openai, silero, cartesia

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "https://n8n-production-141d3.up.railway.app/webhook/real-estate-lead")
logger = logging.getLogger("real-estate-agent")

SYSTEM_PROMPT = """
You are a friendly Real Estate Property Expert for Demo Realty (Kharadi, Pune).
Your job: Qualify leads naturally.

Flow (ask ONE question at a time):
1. Greet: "Hi, thank you for calling Demo Realty, how can I help you today?"
2. Ask BHK: "Are you looking for 1BHK, 2BHK or 3BHK?"
3. Ask Location: "Which location are you interested in? We have in Kharadi, Baner, Wagholi"
4. Ask Budget: "What is your budget range? Like 1Cr, 1.5Cr+?"
5. Ask Timeline: "When are you planning to buy? Immediately or just exploring?"
6. Wrap up: "Perfect, I have noted your requirement. Our expert will share the best 3-4 matched properties on WhatsApp shortly. Can I send the details on this same WhatsApp number?"
7. If user says Yes - confirm: "Great, you will get it in next 2 minutes. Thank you, our expert will call you within 24 hours. Have a great day!"

Rules:
- Be conversational, Hindi + English mix allowed
- If user says "just exploring", tag as COLD, don't push
- Save lead via tool after step 6
"""

async def save_lead_to_sheet(name, phone, bhk, location, budget, timeline, lead_temperature):
    """Send lead to n8n webhook -> Google Sheet"""
    payload = {
        "name": name,
        "phone": phone,
        "BHK": bhk,
        "location": location,
        "budget": budget,
        "timeline": timeline,
        "lead_temperature": lead_temperature
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(N8N_WEBHOOK_URL, json=payload, timeout=10) as resp:
                result = await resp.text()
                logger.info(f"n8n Webhook success: {result}")
                return True
    except Exception as e:
        logger.error(f"n8n Webhook failed: {e}")
        return False

class RealEstateAgent(Agent):
    def __init__(self):
        # Groq uses OpenAI-compatible API, just change base_url + model
        groq_key = os.getenv("GROQ_API_KEY", "")
        deepgram_key = os.getenv("DEEPGRAM_API_KEY", "")
        super().__init__(
            instructions=SYSTEM_PROMPT,
            stt=deepgram.STT(model="nova-2", language="en-IN", api_key=deepgram_key) if deepgram_key else deepgram.STT(model="nova-2", language="en-IN"),
            llm=openai.LLM(
                model="llama-3.1-8b-instant",
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            ),
            tts=cartesia.TTS(model="sonic-english", voice="694f9389-a282-4866-b2a4-18e515254625"),
            vad=silero.VAD.load(),
        )

    async def on_participant_connected(self, participant):
        logger.info(f"Participant connected: {participant.identity}")

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    session = AgentSession(agent=RealEstateAgent())
    await session.start(room=ctx.room)

    @session.on("function_call")
    async def handle_function(event):
        if event.name == "save_lead":
            await save_lead_to_sheet(**event.arguments)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
