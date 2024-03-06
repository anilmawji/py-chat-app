# python-chat-app

P2P file sharing protocol inspired by BitTorrent.

To start a new peer, run `runner.py -port [port_number]`. Once running, use the `help` command to view the list of available commands.

```python
peers     # Display list of peer info
connect -ip [ip_address] -port [port_number]     # Connect to another peer in the network to begin messaging
msg -ip [ip_address] -port [port_number] -text "enter text here"
disconnect     # Disconnect from the peer group
exit    # Close the application
```
