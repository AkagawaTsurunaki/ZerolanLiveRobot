import asyncio

from services.game.minecraft.app import KonekoMinecraftAIAgent

agent = KonekoMinecraftAIAgent()

asyncio.run(agent.start())
