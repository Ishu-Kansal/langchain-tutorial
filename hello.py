from dotenv import load_dotenv, find_dotenv
import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv(), override=True)

@tool
def search(query: str) -> str:
    """
    You are a search tool that can search and return queries over the internet
    
    Input: 
        query: the query to search for
    
    Output:
        the search results
    """
    print("search tool running...\n")
    return "The weather in tokyo is sunny"

llm = ChatOpenAI(temperature=0)
tools = [search]
agent = create_agent(model=llm, tools=tools)

def main():
    print("Hello World")
    result = agent.invoke({'messages': HumanMessage("What is the weather in tokyo today?")})
    print(result)
    
if __name__ == '__main__':
    main()
