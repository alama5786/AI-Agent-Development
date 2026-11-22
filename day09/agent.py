import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

#load the configuration from the .env file
load_dotenv()

# create AI client
client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)   

from day09.agent.mcp_client import (
      connect
    , discover_tool
    , execute_tool
    , disconnect
    )
# define a function to build tool descriptions for the AI model
def build_tool_descriptions(tools):
    tool_descriptions = ""
    for tool in tools:
        tool_descriptions += f"""
        Tool: {tool.name}
        Description: {tool.description}
        """
    return tool_descriptions

def generate_response (user_request, tool_result):
    prompt = f"""
    The user asked:
    {user_request}
    The tool returned:
    {tool_result}
    Respond directly to user in a natural, conversational way.
    Use the tool result as the factual source.
    Transform raw tool output into a human-friendly answer.
    Do not simply copy raw values when a natural sentence would be better
    So not add information that is not needed to answer the request.
    Do not mention tools, internal processing, planning or reasoning.
    Keep the response concise.
    """
    response = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages= [
            {
                "role":"user",
                "content":prompt
            }
        ]

    )
    return response.choices[0].message.content

# define a function to plan the tool execution based on user input and available tools
def planner(user_request, tools):
    # Create tool descriptions for each tool
    tool_descriptions = build_tool_descriptions(tools)

    # Create a prompt by combining the user request and tool descriptions
    prompt = f""" You are an AI Planner.
    Available Tools:
    {tool_descriptions}

    Instructions

    1. Select best tool.
    2. Reply only tool name.
    3. Do not explain.

    User Requst:
    {user_request}
    """

    # Send the prompt to the AI model and get a response
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the tool name and arguments from the AI response
    tool_name  = response.choices[0].message.content.strip()
    return tool_name  # This should be parsed to extract tool name and arguments if needed

# finally, define the main function to orchestrate the steps
async def main():
    # Step1:Connect to the MCP server
    client = await connect()

    # Step2: Discover available tools on the MCP server
    tools = await discover_tool(client)
    print("Available tools on the MCP server:")
    for tool in tools:
        print(f"- {tool.name}")

    # Step3: Planner: Take the user input. 
    # Create tool description for each tool.
    # Then create a prompt by combining the 
    # user input and tool descriptions and give this 
    # prompt to the AI model to get the tool name and 
    # arguments.
    user_request = input("\nYou: ")
    tool_name = planner(user_request, tools)

    print("Planner Selected : ", tool_name)

    # Step4: Execute selected tool
    tool_result = await execute_tool (client, tool_name)

    # Step5: Generate a natural language response
    final_answer = generate_response(user_request, tool_result)
    print(final_answer)

    # Step3: Disconnect from the MCP server
    await disconnect(client)

if __name__ == "__main__":
    asyncio.run(main())