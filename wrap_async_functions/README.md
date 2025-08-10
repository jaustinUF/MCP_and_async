### Wrap async functions in sync functions, and use Streamlit for the frontend. ###

**streamlit_app.py**: creates web page frontend
- uses 'MCPEngine' from 'med_find_engine_shutdown.py' to process query inputs to get response outputs.
- must be run by Streamlit from the terminal

**med_find_engine_shutdown.py**
- wraps async functions (from 'med_find_return.py') in synchronous functions

m**ed_find_return.p**y
- slightly modified version of the MCP client/host 'MCP_chatbot_py' from the 'Model-Context-Protocol-MCP-Project' repo
  - 'process_query' function returns response rather than printing it.



