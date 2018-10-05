import pickle

class RegistrationRequest(object):
    """Encapsulates a registration request from the client."""
    def __init__(self, ip_address, team_name):
        self.ip_address = ip_address
        self.team_name = team_name

class DataResponse(object):
    """Encapsulates a data response to/from the client."""
    def __init__(self, ip_address, data):
        self.ip_address = ip_address
        self.data = data

def registration_process(server, registration_queue):
    """Waits on team registration."""
    while True:
        ip_address, team_name = server.receive_connection_request()
        registration_queue.put(RegistrationRequest(ip_address, team_name))

def incoming_data_process(server, data_queue):
    """Waits on sorted data."""
    while True:
        data, ip_address = server.receive_data()
        up_data = pickle.loads(data)
        data_queue.put(DataResponse(ip_address, up_data))
        
def outgoing_data_process(server, data_queue):
    """Waits on sorted data."""
    while True:
        if data_queue.empty():
            msg = data_queue.get()
            server.send_data(msg.ip_address, msg.data)
            