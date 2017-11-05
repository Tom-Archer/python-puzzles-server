TIMEOUT = 2.0

class Team(object):
    """Encapsulates a team."""
    def __init__(self, name):
        self.name = name
        self.has_data = False
        self.has_row = -1
        self.send_time = 0

class TeamManager(object):
    def __init__(self):
        self.team_dict = {}

    def register(self, ip_address, team_name):
        if ip_address in self.team_dict:
            self.team_dict[ip_address].name = team_name
        else:
            self.team_dict[ip_address] = Team(team_name)

    def allocate(self, ip_address, row):
        if ip_address in self.team_dict:
            self.team_dict[ip_address].has_data = True
            self.team_dict[ip_address].has_row = row
            self.team_dict[ip_address].send_time = time.time()

    def deallocate(self, ip_address):
        if ip_address in self.team_dict:
            self.team_dict[ip_address].has_data = False

    def get_free_team(self):
        free_teams = []
        for ip_address in self.team_dict:
            if not self.team_dict[ip_address].has_data:
                free_teams.append(ip_address)
        return free_teams

    def has_timed_out(self, ip_address):
        if ip_address in self.team_dict:
            if self.team_dict[ip_address].has_data and self.team_dict[ip_address].send_time != 0:
                if (time.time() - self.team_dict[ip_address].send_time) > TIMEOUT:
                    return True
        return False

    def is_allocated(self, ip_address):
        if ip_address in self.team_dict:
            return self.team_dict[ip_address].has_data
        return False

if __name__ == "__main__":
    import ipaddress
    import time
    team_manager = TeamManager()
    ip = ipaddress.ip_address('192.0.2.1') 
    team_manager.register(ip,"team")
    print(team_manager.get_free_team())
    team_manager.allocate(ip, 1)
    print(team_manager.is_allocated(ip))
    time.sleep(TIMEOUT)
    print(team_manager.has_timed_out(ip))
    team_manager.deallocate(ip)
    print(team_manager.is_allocated(ip))
