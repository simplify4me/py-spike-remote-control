import asyncio
from pynput import keyboard

class AsyncKeyboardManager:
    def __init__(self):
        self.pressed_keys = set()
        # Dictionaries to store callbacks: {'key_name': async_function}
        self.callbacks = {
            'press': {},
            'hold': {},
            'release': {}
        }
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()

    def _get_key_name(self, key):
        """Normalize pynput keys to simple strings (e.g., 'a', 'space', 'esc')."""
        try:
            return key.char.lower()
        except AttributeError:
            return key.name.lower()

    def register(self, key_name, event_type, callback):
        """
        Register an async callback for a specific key and event type.
        event_type must be 'press', 'hold', or 'release'.
        """
        if event_type not in self.callbacks:
            raise ValueError("event_type must be 'press', 'hold', or 'release'")
        self.callbacks[event_type][key_name.lower()] = callback

    def on_press(self, key):
        key_name = self._get_key_name(key)

        # If the key is not in our set, it's a new press.
        # If it is, the OS is firing key-repeat events, so it's a hold.
        if key_name not in self.pressed_keys:
            self.pressed_keys.add(key_name)
            self.loop.call_soon_threadsafe(self.queue.put_nowait, ('press', key_name))
        else:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, ('hold', key_name))

    def on_release(self, key):
        key_name = self._get_key_name(key)

        if key_name in self.pressed_keys:
            self.pressed_keys.remove(key_name)
            self.loop.call_soon_threadsafe(self.queue.put_nowait, ('release', key_name))

    async def _process_events(self):
        """Consume events from the queue and dispatch async callbacks."""
        while True:
            event_type, key_name = await self.queue.get()
            print(f"Event: {event_type.upper()} - Key: '{key_name}'")

            # Look up the registered callback
            callback = self.callbacks[event_type].get(key_name)

            if callback:
                # Execute asynchronously without blocking the loop
                asyncio.create_task(callback(key_name, event_type))

    async def run(self):
        """Start the pynput listener and the async event processor."""
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        listener.start()

        print("Keyboard listener started. Press 'esc' to quit.")

        # Run the event processor until cancelled
        event_task = asyncio.create_task(self._process_events())
        try:
            await event_task
        except asyncio.CancelledError:
            listener.stop()

# ==========================================
# Example Usage
# ==========================================

async def long_running_task(key_name, event_type):
    """A simulated long async task that won't block other key presses."""
    print(f"[{event_type.upper()}] '{key_name}' - Starting 2-second async task...")
    await asyncio.sleep(2)
    print(f"[{event_type.upper()}] '{key_name}' - Task finished!")

async def quick_log(key_name, event_type):
    """A quick callback for held or released keys."""
    print(f"[{event_type.upper()}] '{key_name}' detected.")

async def exit_app(key_name, event_type):
    """Stop the event loop."""
    print("\nExiting application...")
    for task in asyncio.all_tasks():
        task.cancel()

async def main():
    manager = AsyncKeyboardManager()

    # Register callbacks for the 'a' key
    manager.register('a', 'press', long_running_task)
    manager.register('a', 'hold', quick_log)
    manager.register('a', 'release', quick_log)

    # Register callbacks for the 'space' key
    manager.register('space', 'press', long_running_task)

    # Escape key to exit cleanly
    manager.register('esc', 'press', exit_app)

    await manager.run()

if __name__ == "__main__":
    # Handle the CancelledError gracefully on exit
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        pass