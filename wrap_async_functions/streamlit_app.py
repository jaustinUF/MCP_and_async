# uses MCPEngine from med_find_engine
import streamlit as st
# from med_find_engine import MCPEngine
from med_find_engine_shutdown import MCPEngine

if "engine" not in st.session_state:
    st.session_state.engine = MCPEngine()
    st.session_state.engine.start()

query = st.text_input("Enter your question")
if st.button("Ask") and query:
    with st.spinner("Thinking..."):
        answer = st.session_state.engine.ask(query)
    st.write(answer or "[No response returned]")

# Optional shutdown button (for local dev)
if st.button("Shutdown Engine"):
    try:
        st.session_state.engine.close()
        st.success("Engine closed.")
    except Exception as e:
        st.error(str(e))


# Terminal: streamlit run wrap_async_functions/streamlit_app.py
