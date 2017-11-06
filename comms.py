
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
