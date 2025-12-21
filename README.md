# LAN Messenger (P2P)

Single-file LAN chat built with Python sockets (UDP broadcast) and a Tkinter GUI. Every peer runs the same script; there is no central server.

## File
- `client.py`: Tkinter peer that listens on a UDP port and broadcasts messages to the LAN.

## Run
On each machine connected to the same LAN/Wi-Fi, launch the client with the same UDP port:
```bash
python client.py --port 5050 --name Alice
```
Then click **Connect** and start chatting. Messages will reach all peers running on that port.

You can prefill the room and private code from CLI as well (the code is never broadcast; other peers must know it to join):
```bash
python client.py --port 5050 --room general --code secret123 --name Alice
```

## UI
- Left panel: discovered rooms (port/room) and a participants list. **Sync** asks peers to re-announce rooms, **Add** opens the room-creation window, **Delete** removes a room only if you created it. Selecting a room shows known participants (requires the correct code for private rooms).
- Room creation window: fields for Port / Room name / Code. **Create the Room** checks the port is free on your machine, saves the room locally, and broadcasts it to peers (without revealing the code).
- Selecting a room fills the fields; set your nickname up top, then **Connect** / **Disconnect**.
- Messages area + input box at bottom.

## Notes
- Traffic is plain text and unencrypted; use only on trusted networks.
- All peers must share the same port and room. If a `Code` is set, only peers using the identical code will see messages (it is not cryptographically secure).
- Ensure your firewall allows UDP on the chosen port.
- The old `server.py` is no longer needed for this P2P mode.
