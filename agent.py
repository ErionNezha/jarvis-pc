# Jarvis PC — LiveKit worker (zë realtime me Gemini)
# RREGULLUAR (2026-10-08): prompts ndërtohen me await build_prompts()
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation

from Jarvis_prompts import build_prompts
from memory_loop import MemoryExtractor
from jarvis_reasoning import thinking_capability
# TË GJITHA komandat direkte në një vend (pa LangChain në mes)
from jarvis_tools import ALL_TOOLS

load_dotenv()


class Assistant(Agent):
    def __init__(self, chat_ctx, instructions) -> None:
        super().__init__(
            chat_ctx=chat_ctx,
            instructions=instructions,
            # Modeli u ndërrua (2026-10-08): Google hoqi gemini-2.0-flash-live-001;
            # modeli aktual live me bidiGenerateContent është 2.5-flash-native-audio.
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-latest",
                voice="Charon",
            ),
            # thinking_capability = LangChain ReAct për arsyetim kompleks;
            # ALL_TOOLS = komandat direkte (hap/mbyll/shkruaj/kërko/mot/orë/volum).
            tools=[thinking_capability] + ALL_TOOLS,
        )


async def entrypoint(ctx: agents.JobContext):
    # Çdo /token krijon dhomë unike → dublikatat janë të pamundura.
    instructions_prompt, reply_prompts = await build_prompts()

    session = AgentSession(preemptive_generation=True)
    current_ctx = session.history.items

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=current_ctx, instructions=instructions_prompt),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await session.generate_reply(instructions=reply_prompts)

    conv_ctx = MemoryExtractor()
    await conv_ctx.run(current_ctx)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        # Emri i agentit — token_server.py e thërret me këtë emër në dhomë
        # (explicit dispatch; 1.2.1 s'ka auto-dispatch).
        agent_name="jarvis-agent",
    ))
