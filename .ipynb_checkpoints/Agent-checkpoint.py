{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "e9b56473-2e02-4382-a39e-47c70ad0734e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Writing Agent.py\n"
     ]
    }
   ],
   "source": [
    "%%writefile Agent.py\n",
    "import os\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "load_dotenv()\n",
    "\n",
    "GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "411eef93-4b4a-438f-830e-8af7d9fb3102",
   "metadata": {},
   "outputs": [],
   "source": [
    "from langchain_google_genai import ChatGoogleGenerativeAI\n",
    "\n",
    "llm = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash', temperature=0, google_api_key = GOOGLE_API_KEY)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "c8a07114-9d03-4524-8979-99022c344044",
   "metadata": {},
   "outputs": [],
   "source": [
    "import asyncio\n",
    "from langchain_mcp_adapters.client import MultiServerMCPClient\n",
    "\n",
    "async def main():\n",
    "    client = MultiServerMCPClient({\n",
    "        \"local\": {\n",
    "            \"command\": \"uv\",\n",
    "            \"args\": [\"run\", \"mcpserver.py\"],\n",
    "            \"transport\": \"stdio\"\n",
    "        }\n",
    "    })\n",
    "    \n",
    "    tools = await client.get_tools()\n",
    "\n",
    "    print(tools)\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "ae2fae14-3bd5-4b26-957d-6605aa55df81",
   "metadata": {},
   "outputs": [
    {
     "ename": "RuntimeError",
     "evalue": "asyncio.run() cannot be called from a running event loop",
     "output_type": "error",
     "traceback": [
      "\u001b[31m---------------------------------------------------------------------------\u001b[39m",
      "\u001b[31mRuntimeError\u001b[39m                              Traceback (most recent call last)",
      "\u001b[36mCell\u001b[39m\u001b[36m \u001b[39m\u001b[32mIn[5]\u001b[39m\u001b[32m, line 1\u001b[39m\n\u001b[32m----> \u001b[39m\u001b[32m1\u001b[39m \u001b[43masyncio\u001b[49m\u001b[43m.\u001b[49m\u001b[43mrun\u001b[49m\u001b[43m(\u001b[49m\u001b[43mmain\u001b[49m\u001b[43m(\u001b[49m\u001b[43m)\u001b[49m\u001b[43m)\u001b[49m\n",
      "\u001b[36mFile \u001b[39m\u001b[32m/opt/anaconda3/lib/python3.11/asyncio/runners.py:186\u001b[39m, in \u001b[36mrun\u001b[39m\u001b[34m(main, debug)\u001b[39m\n\u001b[32m    161\u001b[39m \u001b[38;5;250m\u001b[39m\u001b[33;03m\"\"\"Execute the coroutine and return the result.\u001b[39;00m\n\u001b[32m    162\u001b[39m \n\u001b[32m    163\u001b[39m \u001b[33;03mThis function runs the passed coroutine, taking care of\u001b[39;00m\n\u001b[32m   (...)\u001b[39m\u001b[32m    182\u001b[39m \u001b[33;03m    asyncio.run(main())\u001b[39;00m\n\u001b[32m    183\u001b[39m \u001b[33;03m\"\"\"\u001b[39;00m\n\u001b[32m    184\u001b[39m \u001b[38;5;28;01mif\u001b[39;00m events._get_running_loop() \u001b[38;5;129;01mis\u001b[39;00m \u001b[38;5;129;01mnot\u001b[39;00m \u001b[38;5;28;01mNone\u001b[39;00m:\n\u001b[32m    185\u001b[39m     \u001b[38;5;66;03m# fail fast with short traceback\u001b[39;00m\n\u001b[32m--> \u001b[39m\u001b[32m186\u001b[39m     \u001b[38;5;28;01mraise\u001b[39;00m \u001b[38;5;167;01mRuntimeError\u001b[39;00m(\n\u001b[32m    187\u001b[39m         \u001b[33m\"\u001b[39m\u001b[33masyncio.run() cannot be called from a running event loop\u001b[39m\u001b[33m\"\u001b[39m)\n\u001b[32m    189\u001b[39m \u001b[38;5;28;01mwith\u001b[39;00m Runner(debug=debug) \u001b[38;5;28;01mas\u001b[39;00m runner:\n\u001b[32m    190\u001b[39m     \u001b[38;5;28;01mreturn\u001b[39;00m runner.run(main)\n",
      "\u001b[31mRuntimeError\u001b[39m: asyncio.run() cannot be called from a running event loop"
     ]
    }
   ],
   "source": [
    "asyncio.run(main())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "b4069159-d15b-47c0-8eea-c00c189fb629",
   "metadata": {},
   "outputs": [],
   "source": [
    "from langgraph.graph import START, END, StateGraph\n",
    "from typing import TypedDict, Annotated\n",
    "from langgraph.graph.message import add_messages\n",
    "\n",
    "class MessagesState(TypedDict):\n",
    "    messages: Annotated[list[str], add_messages]\n",
    "\n",
    "\n",
    "# Creating React type agent\n",
    "builder = StateGraph(MessagesState)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3900cb5b-1b1c-4571-a6f9-0a43c97505cd",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Construction",
   "language": "python",
   "name": "construction"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
