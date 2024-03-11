import bencode
import math
from piece import Piece

class Torrent():
    def __init__(self, file_name = '', tracker_endpoints = [], total_length = 0, piece_length = 0, pieces = [], pieces_count = 0):
        self.file_name = file_name
        self.tracker_endpoints = tracker_endpoints  # List of tuples - (ip_address, port) each taken from a tracker url (urls are extracted from announce-list in metadata - to start, support only HTTP URLs)
        self.total_length = total_length  # Total file length in bytes
        self.piece_length = piece_length  # Piece size in bytes
        self.pieces = pieces              # Concatenation of all 20-byte SHA1 hash values
        self.pieces_count = pieces_count  # Number of required pieces: int(len(self.total_length) / self.piece_length)


    # Read .torrent metadata from a bencoded file
    @staticmethod
    def read_metadata(file_path: str) -> 'Torrent':
        with open(file_path, 'rb') as torrentfile:
            if not torrentfile:
                print(f"Error: File {file_path} not found")
                return None
            contents = bencode.decode(torrentfile.read())

        print(f"Contents: {contents}")
        info = contents.get('info')
        print(f"pieces: {info.get('pieces')}")
        return Torrent(
            file_name=info.get('name'),
            tracker_endpoints=Torrent.create_tracker_list(contents.get('announce')),
            total_length=info.get('length'),
            piece_length=info.get('piece length'),
            pieces=Torrent.create_pieces(info.get('pieces'), info.get('piece length')),
            pieces_count=math.ceil(info.get('length') / info.get('piece length'))
        )
    
    
    @staticmethod
    def create_tracker_list(tracker_list: list):
        tracker_tuples = []

        for tracker in tracker_list:
            _, tracker_address, tracker_port = tracker.split(':')
            tracker_address = tracker_address[2:]
            tracker_tuples.append((tracker_address, int(tracker_port)))

        return tracker_tuples


    @staticmethod
    def create_pieces(pieces, piece_length) -> list:
        pieces_list = []

        for index, piece_hash in enumerate(pieces):
            pieces_list.append(Piece(index, piece_length, piece_hash))
            
        return pieces_list
    