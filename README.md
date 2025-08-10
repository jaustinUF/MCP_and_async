# MCP and async #

### Problem ###
 Initial attempts to use Streamlit as the frontend for a MCP client/host ('MCP_Chatbot' in Model Context Protocol (MCP) Project repo) met with failure, often with unexpected/unknown error messages. Subsequent research, testing, and debugging uncovered several issues:
- the protocol standard 'Model Context Protocol' is language/framework agnostic; libraries for MCP are not.
- the major Python MCP library (pip 'mcp' package, maintained by Anthropic personnel) makes heavy use of asynchronous programming via the asyncio library. (https://github.com/modelcontextprotocol/python-sdk/tree/main)
- Python frontend frameworks (particularly Streamlit with its 're-render-on-every-change' design), do not 'play well' in the async environment.

### Solutions ###
The scripts in this repo use two patterns to 'unhook' the frontend from the MCP client:
- brute-force: wrap the async functions in synchronous functions
  - these scripts are in the 'wrap_async_functions' directory, using a Streamlit frontend.
- elegant (more complex): runs sync and async processes in separate threads; inter-thread communication is via queues.
  - these scripts are in the 'NiceGUI_med_find' directory, using a NiceGUI frontend.  

The README.md in each directory has more detail. 

### Notes ###
To run these scripts, two additional files are needed:
- research_server.py: local server to find and get information from the research paper archive 'arXiv'.
- server_config.json: configuration file used by the client to find and load servers.



