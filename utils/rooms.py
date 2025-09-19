


class Room:
    def __init__(self,room_id:str):
        self.room = room_id
        self.active_connections = set()

    def add_connection(self,websocket:WebSocket):
        self.active_connections.add(websocket)

    def remove_connection(self,websocket:WebSocket):
        self.active_connections.remove(websocket)

    def get_connections(self):
        return self.active_connections
    
    async def broadcast(self,message:dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.remove_connection(connection)