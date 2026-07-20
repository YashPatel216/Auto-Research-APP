from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrap_url
import os 
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile", temperature=0.2, max_tokens=2000)
def build_search_agent():
    return create_react_agent(
        model=llm,
        tools=[web_search]
    )

def build_scrap_agent():
    return create_react_agent(
        model=llm,
        tools=[scrap_url]
    )


## Writer Chain

writer_prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are an expert writer and researcher. You will be given a topic and you will write a detailed article on the topic using the information provided by the user. You will also use your own knowledge to add more information to the article. The article should be well structured and should have a clear introduction, body and conclusion. The article should be written in a professional tone and should be free of grammatical errors. The article should be at least 1000 words long."),
        ("human",""""You are given the following information. Please write a detailed article using the information provided.".
    
    Topic: {topic}
    Reseach Gathered:{research}
    Stuctured The Report as :
    -Introduction
    -Key Findings (Minimum 3 Well Explained points)
    -conclusion
    -Sources(List all URLs found in research)
         Be Detailed,Factual and professional."""),

])


writer_chain = writer_prompt | llm | StrOutputParser()


##critic Chain

critic_prompt=ChatPromptTemplate.from_messages([
    ("system","You are an expert critic and researcher. You will be given a topic and you will write a detailed critique on the topic using the information provided by the user. You will also use your own knowledge to add more information to the critique. The critique should be well structured and should have a clear introduction, body and conclusion. The critique should be written in a professional tone and should be free of grammatical errors. The critique should be at least 1000 words long."),
    ("human", """You are given the following information on the topic: . Please write a detailed critique on the topic using the information provided. You can also use your own knowledge to add more information to the critique. The critique should be well structured and should have a clear introduction, body and conclusion. The critique should be written in a professional tone and should be free of grammatical errors. The critique should be at least 1000 words long.

    Report: {report}
    Reseach Gathered:{research}
    Report in the exact Format as :
    Score:x/10
    Strengths:
    -...
    -...
     
    Areas To Improvement:
    -...
    -...
    One line verdict on the report and a detailed explanation of the score given. Be Detailed,Factual and professional."""),     
])

critic_chain = critic_prompt | llm | StrOutputParser()