"""
Example program for computer-to-hub communication.
Requires Pybricks firmware >= 3.3.0.
"""

import asyncio
import aioconsole
import sys
from contextlib import suppress
from bleak import BleakScanner, BleakClient
from sshkeyboard import listen_keyboard_manual

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Replace with your hub's BLE name (default is usually "Pybricks Hub")
HUB_NAME = "Pybricks Hub"

async def main():
    main_task = asyncio.current_task()

    def handle_disconnect(_):
        print("Hub was disconnected.")
        if not main_task.done():
            main_task.cancel()

    ready_event = asyncio.Event()

    def handle_rx(_, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event
            payload = data[1:]
            if payload == b"rdy":
                ready_event.set()
            else:
                print("Receive:", payload)

    # Scan for the hub
    device = await BleakScanner.find_device_by_name(HUB_NAME)
    if device is None:
        print(f"Could not find hub with name: {HUB_NAME}")
        return

    # Connect
    async with BleakClient(device, handle_disconnect) as client:

        async def send(data):
            # Wait for hub to signal it's ready
            #await ready_event.wait()
            #ready_event.clear()
            # Prepend 0x06 = "write stdin" command
            print(f"Key pressed : {data}")
            await client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data.encode('utf-8'),
                response=True
            )

        # Subscribe to hub notifications
        await client.start_notify(
            PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx
        )

        print("Start the program on the hub now with the button.")

        # --- Main loop: read keyboard input and send to hub ---
        await asyncio.gather(
            listen_keyboard_manual(on_press=send))

if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())