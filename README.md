# python-chat-app

P2P file sharing protocol inspired by BitTorrent.

To start a new peer, run `runner.py -port [port_number]`. Once running, use the `help` command to view the list of available commands.

```python
# Display list of peer info
peers
# Connect to another peer in the network to begin messaging
connect -ip [ip_address] -port [port_number]
# Send a message to another peer
msg -ip [ip_address] -port [port_number] -text "enter text here"
# Disconnect from the peer group
disconnect
# Close the application
exit
```
