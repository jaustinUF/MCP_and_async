import asyncio
import threading
from typing import Optional

from med_find_return import MCP_ChatBot  # ensure filename matches

class MCPEngine:
    """
    Persistent sync wrapper around the async MCP client.
    Starts a background event loop + one runner task that:
      - connects (open async contexts)
      - waits for a shutdown event
      - cleans up (close async contexts)
    Connect and cleanup happen in the SAME task (fixes anyio cancel-scope error).
    """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

        # Objects that live on the loop
        self._runner_task: Optional[asyncio.Task] = None
        self._shutdown_evt: Optional[asyncio.Event] = None
        self._ready_fut: Optional[asyncio.Future] = None

        # Exposed bot reference (valid only while started)
        self.bot: Optional[MCP_ChatBot] = None

        self._closed = False

    # ---------- internal helpers ----------

    def _submit(self, coro, timeout: Optional[float] = None):
        """Submit a coroutine to the loop and wait synchronously for the result."""
        if self._closed:
            raise RuntimeError("Engine is closed.")
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return fut.result(timeout=timeout)

    async def _runner(self):
        """
        Runs entirely on the event loop thread.
        Open async contexts (connect), wait for shutdown, then cleanup.
        """
        self.bot = MCP_ChatBot()
        try:
            await self.bot.connect_to_servers()
        except Exception as e:
            # Signal failure to the starter and re-raise
            if self._ready_fut and not self._ready_fut.done():
                self._ready_fut.set_exception(e)
            raise
        else:
            # Signal that we're ready
            if self._ready_fut and not self._ready_fut.done():
                self._ready_fut.set_result(True)

        # Wait for shutdown request
        try:
            await self._shutdown_evt.wait()
        finally:
            # Cleanup MUST happen in the same task that opened contexts
            try:
                await self.bot.cleanup()
            finally:
                self.bot = None

    # ---------- public API (sync) ----------

    def start(self, timeout: float = 60.0):
        """
        Start the engine and connect to servers.
        Blocks until connections are ready or timeout.
        """
        if self._closed:
            raise RuntimeError("Engine is closed.")
        if self._runner_task and not self._runner_task.done():
            return  # already started

        async def _start():
            self._shutdown_evt = asyncio.Event()
            self._ready_fut = self.loop.create_future()
            self._runner_task = asyncio.create_task(self._runner())
            # Wait until runner signals readiness (or failure)
            await self._ready_fut

        return self._submit(_start(), timeout=timeout)

    def ask(self, query: str, timeout: Optional[float] = None) -> str:
        """Synchronously ask a question; returns the model's final text."""
        if self._closed or not self._runner_task or self._runner_task.done():
            raise RuntimeError("Engine is not running. Call start() first.")

        async def _ask():
            return await self.bot.process_query(query)

        return self._submit(_ask(), timeout=timeout)

    def close(self, timeout: float = 30.0):
        """
        Signal the runner to shut down, wait for cleanup to finish,
        then stop the loop thread.
        Safe to call once; subsequent calls are no-ops.
        """
        if self._closed:
            return

        async def _close():
            if self._runner_task:
                if self._shutdown_evt and not self._shutdown_evt.is_set():
                    self._shutdown_evt.set()
                # Wait for runner to finish cleanup
                try:
                    await asyncio.wait_for(self._runner_task, timeout=timeout)
                finally:
                    self._runner_task = None

        try:
            # Perform shutdown on the loop so it's in the same task context
            self._submit(_close(), timeout=timeout + 5)
        finally:
            # Stop the loop and join the thread
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=2)
            self._closed = True
