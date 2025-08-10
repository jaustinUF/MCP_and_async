### Use threads/queues to separate async, and use NiceGUI for the frontend ###

**med_find_nicegui_frontend.py**: creates web page frontend
- 'AsyncWorker' thread for MCP processing
  - ('start_async_loop' in 'med_find_sync_bridge2.py')
  - replaces stdio with web page.
- avoids blocking MainThread functions (spinner, output, etc.)
- this script essentially replaces the 'main' functions in 'med_find_sync_bridge2.py'

**med_find_sync_bridge2.py**
- engine for backend MCP processing
- this script can be run stand-alone
  - synchronous 'main' function
  - 'AsyncWorker' thread for MCP processing ('start_async_loop')
