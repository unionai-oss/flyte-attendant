from langchain.llms import OpenAI

llm = OpenAI(temperature=0.9)

text = """..."""
print(llm(text))
