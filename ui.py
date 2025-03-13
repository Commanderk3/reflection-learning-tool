import streamlit as st
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

if 'messages' not in st.session_state:
    st.session_state.messages = [SystemMessage(instruction)]

st.title("Reflective Learning Session")

user_input = st.text_input("You:", "")
if st.button("Send") and user_input.strip():
    if user_input.lower() == "exit":
        st.session_state.end_session = True
    else:
        st.session_state.messages.append(HumanMessage(user_input))

        # Retrieve context
        relevant_docs = getContext(user_input)

        # Combine context and conversation
        def combined_input(rag, messages):
            conversation_history = ""
            for msg in messages:
                if isinstance(msg, SystemMessage):
                    conversation_history += f"System: {msg.content}\n"
                elif isinstance(msg, HumanMessage):
                    conversation_history += f"User: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    conversation_history += f"Assistant: {msg.content}\n"
            return f"Context: {rag}\nConversation History:\n{conversation_history}\nAssistant:"

        # Stream AI response
        full_response = ""
        with st.spinner("AI is thinking..."):
            for chunk in llm.stream(combined_input(relevant_docs, st.session_state.messages)):
                response_piece = chunk.content
                if response_piece:
                    full_response += response_piece

        st.session_state.messages.append(AIMessage(full_response))
        st.write(f"AI: {full_response}")

# End session
if st.session_state.get('end_session'):
    st.success("Session ended by user")

    def generate_summary(messages):
        user_queries = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
        assistant_responses = [msg.content for msg in messages if isinstance(msg, AIMessage)]
        summary_prompt = f"""
        Analyze the following conversation and generate a concise summary for the User's learning and takeaways.
        User Queries: {user_queries}\nAssistant Responses: {assistant_responses}\nSummary:
        """
        return llm.invoke(summary_prompt)

    summary = generate_summary(st.session_state.messages)
    st.subheader("📝 Conversation Summary")
    st.write(summary.content)

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
        return llm.invoke(analysis_prompt)

    outcome = analysis(old_summary, summary.content)
    st.subheader("📊 Development Insights")
    st.write(outcome.content)

    old_summary = outcome.content
    st.session_state.messages = [SystemMessage(instruction)]