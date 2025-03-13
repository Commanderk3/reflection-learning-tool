import config
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from retriever import getContext

embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

db = Chroma(persist_directory=config.CHROMA_DB_DIR, embedding_function=embeddings)

llm = ChatOllama(
    base_url=config.URL,
    model=config.LLM_MODEL,
    streaming=True,
    temperature=0.7,
    stop=["User:", "System:"]
)

old_summary = """
Let's summarize what we've discussed so far:
You created a project in Music Blocks and made a cool hip-hop beat. You used the Pitch-Drum Matrix to experiment with different rhythms and patterns, which allowed you to think freely and focus on the creative aspect.
You learned that trying different patterns is not the only thing to focus on when creating a beat, and that splitting a note value can lead to some really cool and unique sounds.
You're planning to create a chord progression that suits your beat and wants to enhance or complement its vibe.
"""

instruction = """
You are a teacher within the MusicBlocks platform. Your role is to engage users in a deep, introspective dialogue that promotes conceptual learning and self-improvement.
Your approach is both analytical, aimed at understanding the user's actions and guiding them toward meaningful insights. WORD LIMIT: 30.
Key Responsibilities:
1. Sequential Inquiry:
   Ask unique, open-ended questions per in the following order:
     1. What did you do?
     2. Why did you do it?
     3. How did you choose to solve the problem and why only this approach?
     4. Ask technical questions based on the answer and context provided. Discuss different approaches to solve this problem.
     5. What did you learn from the experience?
     6. What might you do next?
(Q4. is important)
2. Avoid repeating similar questions or statements. Tailor your responses based on the context and previous exchanges, ensuring each interaction feels fresh and contextually appropriate.
3. Leverage any provided context to enhance the relevance and depth of your questions. If a user references past experiences or details, integrate that information into your follow-up inquiries and teachings.
4. If the conversation diverges from the topic, ask the user to stay on topic.
5. Complete all the questions under 10 AI-messages.
6. Ask only Questions.
7. Dont't ask about previous projects focus only on the current one.
"""


messages = [
    SystemMessage(instruction)
]

def combined_input(rag, messages):

    conversation_history = ""
    for msg in messages:
        if isinstance(msg, SystemMessage):
            conversation_history += f"System: {msg.content}\n"
        elif isinstance(msg, HumanMessage):
            conversation_history += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            conversation_history += f"Assistant: {msg.content}\n"
        else:
            conversation_history += f"{msg.content}\n"
    prompt = f"Context: {rag}\nConversation History:\n{conversation_history}\nAssistant:"
    return prompt

def generate_summary(messages):

    user_queries = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
    assistant_responses = [msg.content for msg in messages if isinstance(msg, AIMessage)]

    summary_prompt = f"""
    Analyze the following conversation and generate a concise summary for the User's learning and takeaways.
    Add only relevant information in this summary. Write a paragraph under 60 words.

    User Queries:
    {user_queries}

    Assistant Responses:
    {assistant_responses}

    Summary:
    """
    summary = llm.invoke(summary_prompt)
    return summary

def analysis(old_summary, new_summary):
    analysis_prompt = f"""
    Analyze the user's learning by comparing the following two summaries. Identify key improvements, knowledge growth, and any remaining gaps.
    Provide constructive assessment of the user's development over time in a paragraph under 50 words.

    Previous Summary:
    {old_summary}

    Current Summary:
    {new_summary}

    Learning Outcome:
    """
    outcome = llm.invoke(analysis_prompt)
    return outcome

# Session loop
while True:
    try:
        query = input("You: ").strip()
        if not query:
            print("⚠️ Please enter a valid query.")
            continue
        if query.lower() == "exit":
            break

        relevant_docs = getContext(query)
        if not relevant_docs:
            print("⚠️ No relevant documents found.")

        messages.append(HumanMessage(query))

        # Stream AI response
        full_response = ""
        print("AI: ")
        for chunk in llm.stream(combined_input(relevant_docs, messages)):
            response_piece = chunk.content
            if response_piece:
                print(response_piece, end="", flush=True)
                full_response += response_piece
        print()

        messages.append(AIMessage(content=full_response))

    except Exception as e:
        print(f"⚠️ Error: {e}")

# Generate and display the conversation summary
summary = generate_summary(messages)
print("\n📝 Conversation Summary:")
print(summary.content)

outcome = analysis(old_summary, summary)
print("\n📝 Developmet Insights:")
print(outcome.content)
old_summary = outcome #replace old summary
messages = []

# while True:
#     try:
#         query = input("You: ")
#         if query.lower() == "exit":
#             break

#         # Retrieve relevant documents
#         relevant_docs = retriever.invoke(query)
#         rag_context = " ".join(doc.page_content for doc in relevant_docs) if relevant_docs else "No relevant documents found."

#         # Append user message
#         messages.append(HumanMessage(query))

#         # Get AI response
#         result = llm.invoke(combined_input(rag_context, messages))
#         response = result.content
#         if response.lower() == "exit":
#             break

#         # Append AI message
#         messages.append(AIMessage(content=response))

#         print(f"AI: {response}")

#     except Exception as e:
#         print(f"⚠️ Error: {e}")

