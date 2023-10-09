import openai
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain, SequentialChain
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.memory import ConversationBufferMemory


def practice():
    prompt = PromptTemplate.from_template("What is the capital of {place}?")
    llm = OpenAI(temperature=0.3)

    chain = LLMChain(llm=llm, prompt=prompt)

    city = "New York City"
    output = chain.run(city)
    print(output)


# LLM to get name of an e commerce store from a product name

prompt = PromptTemplate.from_template("What is the name of the e commerce store that sells {product}?")
llm = OpenAI(temperature=0.3)
chain1 = LLMChain(llm=llm, prompt=prompt)


# LLM to get comma separated names of products from an e commerce store name
prompt = PromptTemplate.from_template("What are the names of the products at {store}?")
llm = OpenAI(temperature=0.3)
chain2 = LLMChain(llm=llm, prompt=prompt)



# Create an overall chain from simple sequential chain
chain = SimpleSequentialChain(
    chains=[chain1, chain2]
)



# An example of Sequential chain
# This is an LLMChain to write a synopsis given a title of a play and the era it is set in.
llm = OpenAI(temperature=.7)
template = """You are a playwright. Given the title of play and the era it is set in, it is your job to write a synopsis for that title.

Title: {title}
Era: {era}
Playwright: This is a synopsis for the above play:"""
prompt_template = PromptTemplate(input_variables=["title", "era"], template=template)
synopsis_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="synopsis")

# This is an LLMChain to write a review of a play given a synopsis.
llm = OpenAI(temperature=.7)
template = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.

Play Synopsis:
{synopsis}
Review from a New York Times play critic of the above play:"""
prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
review_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="review")

# This is the overall chain where we run these two chains in sequence.

overall_chain = SequentialChain(
    chains=[synopsis_chain, review_chain],
    input_variables=["era", "title"],
    # Here we return multiple variables
    output_variables=["synopsis", "review"],
    verbose=True)



# Agent Demo
llm = OpenAI(temperature=.7)
tools = load_tools(["wikipedia", "llm-math"], llm=llm)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


# Memory in LLMs
llm = OpenAI(temperature=0.3)
prompt = PromptTemplate.from_template("What is the name of the e commerce store that sells {product}?")
chain = LLMChain(llm=llm, prompt=prompt, memory=ConversationBufferMemory())
output = chain.run("fruits")
output = chain.run("books")
print(chain.memory.buffer)
print(output)