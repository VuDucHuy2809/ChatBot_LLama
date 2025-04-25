from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from classify_prompts import classify_input
from llm import llm
###
def get_answer(response: str) -> str:
    response = response.lower()
    chain = (RunnableLambda(classify_input) 
        | llm
        | StrOutputParser()
        )
    answer = chain.invoke(response)
    return answer
###