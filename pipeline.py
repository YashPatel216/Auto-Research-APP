from agents import build_search_agent, build_scrap_agent, writer_chain, critic_chain
from rich import print

def run_research_pipeline(topic:str)->dict:
    state={}

    ## seacrch agent working
    print("\n="+"="*50)
    print("Step 1 Search Agent is working....")
    print("="*50)

    search_agent=build_search_agent()
    search_result=search_agent.invoke(
        {
            "messages":[
                ("user",f"Please search the web for research and reliable information on the topic: {topic}.")

            ]
        }
    )
    state["search_result"]=search_result['messages'][-1].content
    print("\n Search result\n",state["search_result"])

    ## scrap agent working
    print("\n="+"="*50)
    print("Step 2 reader Agent is scraping....")
    print("="*50)
    reader_agent=build_scrap_agent()
    reader_result=reader_agent.invoke({
        "messages":[
        ("user",
        f"Based on the following research results about {topic}. "
        f"Pick the most relevant URLs and scrape them for deeper content on {topic}. "
        f"Search results:\n{state['search_result'][:800]}"   
        )] 
    })  
    state["scraped_Content"]=reader_result['messages'][-1].content
    print("\n Scraped Content",state["scraped_Content"])


    ## writer chain working
    print("\n="+"="*50)
    print("Step 3 Writer Chain is working....")
    print("="*50)

    research_combined=(
        f"SEARCH RESULT:\n{state['search_result']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_Content']}"
    )
    state ["report"]=writer_chain.invoke(
        {"topic":topic,
         "research":research_combined,
        }   
    )

    print("\n Report Generated",state["report"])


    ### critic chain working
    print("\n="+"="*50)
    print("Step 4 Critic Chain is working....")
    print("="*50)

    state["Feedback"]=critic_chain.invoke( {
        "report":state["report"],
        "research":research_combined
    })

    print("\n Feedback Generated",state["Feedback"])

    return state


if __name__== "__main__":
    topic=input("\n Enter a Research Topic:")
    run_research_pipeline(topic)