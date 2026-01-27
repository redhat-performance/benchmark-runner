import os
import asyncio
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from contextlib import AsyncExitStack
from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.sse import sse_client

# 0. Core setup
nest_asyncio.apply()
load_dotenv()

# --- CONFIGURATION ---
MODEL_NAME = os.getenv("MODEL_NAME")
MCP_SSE_URL = os.getenv("MCP_SSE_URL")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    st.error("⚠️ Missing GEMINI_API_KEY in .env file!")
    st.stop()

client = genai.Client(api_key=GEMINI_KEY)


# --- 1. THE SCHEMA CLEANER (Stability Fix) ---
def fix_gemini_schema(schema: dict):
    if not isinstance(schema, dict):
        return {"type": str(schema)}
    cleaned = {}
    raw_type = schema.get("type")
    cleaned["type"] = raw_type[0] if isinstance(raw_type, list) else (raw_type or "object")
    if "description" in schema:
        cleaned["description"] = schema["description"]
    if cleaned["type"] == "array":
        cleaned["items"] = fix_gemini_schema(schema["items"]) if "items" in schema else {"type": "string"}
    if "properties" in schema and isinstance(schema["properties"], dict):
        cleaned["properties"] = {k: fix_gemini_schema(v) for k, v in schema["properties"].items()}
    if "required" in schema:
        cleaned["required"] = schema["required"]
    return cleaned


# --- 2. MCP ASYNC HANDLERS ---
async def fetch_tools_dynamically():
    async with AsyncExitStack() as stack:
        try:
            read, write = await stack.enter_async_context(sse_client(MCP_SSE_URL))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            mcp_data = await session.list_tools()
            return [
                types.FunctionDeclaration(
                    name=t.name,
                    description=t.description or "No description",
                    parameters=fix_gemini_schema(t.inputSchema)
                ) for t in mcp_data.tools
            ]
        except Exception as e:
            st.error(f"MCP Connection Failed: {e}")
            return []


async def execute_tool(name, args):
    try:
        async with AsyncExitStack() as stack:
            read, write = await stack.enter_async_context(sse_client(MCP_SSE_URL))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            result = await session.call_tool(name, args)
            return "\n".join([c.text for c in result.content if hasattr(c, 'text')])
    except Exception as e:
        return f"Error: {str(e)}"


# --- 3. STREAMLIT UI & SESSION RESET ---
st.set_page_config(page_title="Gemini PerfCi Agent", page_icon="🤖", layout="wide")

# RESET BUTTON (Clears history and forces a fresh tool sync)
if st.sidebar.button("🧹 Reset All (Clean Cache)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("🧩 PerfCi Data Analyst")
st.caption("based on ElasticSearch Data")

# Only fetch tools if they don't exist in the current clean session
if "gemini_tool" not in st.session_state:
    with st.spinner("🔄 Syncing MCP Tools..."):
        decls = asyncio.get_event_loop().run_until_complete(fetch_tools_dynamically())
        st.session_state.gemini_tool = types.Tool(function_declarations=decls) if decls else None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display current session messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. THE AGENTIC LOOP ---
if prompt := st.chat_input("Ask for PerfCI results..."):
    # 1. Immediate UI Feedback
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Agent Reasoning Turn
    with st.chat_message("assistant"):
        history = [types.Content(role="model" if m["role"] == "assistant" else "user",
                                 parts=[types.Part(text=m["content"])]) for m in st.session_state.messages]

        SYSTEM_INSTRUCTION = """You are an autonomous ElasticSearch investigator.
        Your goal is to find specific data points (like MSSQL results, OCP versions).
        Use `list_indices` and `get_mapping` to understand the server structure.
        DO NOT guess field names. Verify them first."""

        # Investigation spinner only appears AFTER a prompt is sent
        with st.spinner("🤖 Agent is investigating..."):
            MAX_TURNS = 10
            final_answer = ""

            for turn in range(MAX_TURNS):
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=history,
                        config=types.GenerateContentConfig(
                            tools=[st.session_state.gemini_tool] if st.session_state.gemini_tool else None,
                            system_instruction=SYSTEM_INSTRUCTION
                        )
                    )

                    res_content = response.candidates[0].content
                    history.append(res_content)
                    fcalls = [p.function_call for p in res_content.parts if p.function_call]

                    if not fcalls:
                        final_answer = response.text
                        break

                    # Execute tool calls silently
                    t_responses = []
                    for fc in fcalls:
                        output = asyncio.get_event_loop().run_until_complete(execute_tool(fc.name, fc.args))
                        t_responses.append(
                            types.Part(function_response=types.FunctionResponse(
                                name=fc.name, response={"result": output}
                            ))
                        )
                    history.append(types.Content(role="user", parts=t_responses))

                except Exception as e:
                    st.error(f"Logic Interrupted: {e}")
                    break

        if final_answer:
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
