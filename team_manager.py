import time

TIMEOUT = 2.0

class Team(object):
    """Encapsulates a team."""
    def __init__(self, name):
        self.name = name
        self.has_data = False
        self.has_row = -1
        self.send_time = 0

    def __str__(self):
        return (self.name[:15] + '..') if len(self.name) > 15 else self.name
    
class TeamManager(object):
    """Manages team registrations, row allocation and deallocation."""
    def __init__(self):
        self.team_dict = {}

    def register(self, ip_address, team_name):
        """Register a team name to a given IP address."""
        if ip_address in self.team_dict:
            self.team_dict[ip_address].name = team_name
        else:
            self.team_dict[ip_address] = Team(team_name)

    def allocate(self, ip_address, row_id):
        """Allocate a row number to an IP address."""
        if ip_address in self.team_dict:
            self.team_dict[ip_address].has_data = True
            self.team_dict[ip_address].has_row = row_id
            self.team_dict[ip_address].send_time = time.time()

    def deallocate(self, ip_address):
        """Remove an allocated row number from an IP address."""
        if ip_address in self.team_dict:
            if self.team_dict[ip_address].has_data:
                self.team_dict[ip_address].has_data = False
                return self.team_dict[ip_address].has_row
        return None

    def get_registered_teams(self):
        """Return a list of all the registered IP addresses."""
        return list(self.team_dict.keys())

    def get_free_teams(self):
        """Return a list of IP addresses without data."""
        free_teams = []
        for ip_address in self.team_dict:
            if not self.team_dict[ip_address].has_data:
                free_teams.append(ip_address)
        return free_teams

    def get_timed_out_teams(self):
        """Return a list of teams who have not returned data."""
        timed_out_teams = []
        for ip_address in self.team_dict:
            if self.team_dict[ip_address].has_data and self.team_dict[ip_address].send_time != 0:
                if (time.time() - self.team_dict[ip_address].send_time) > TIMEOUT:
                    timed_out_teams.append(ip_address)
        return timed_out_teams

    def get_team_name(self, ip_address):
        """Get the team name for a given IP address."""
        if ip_address in self.team_dict:
            return str(self.team_dict[ip_address])
        return None

    def reset_allocations(self):
        """Reset all allocations."""
        for ip_address in self.team_dict:
            team = self.team_dict[ip_address]
            team.has_data = False
            team.send_time = 0

if __name__ == "__main__":
    import ipaddress
    team_manager = TeamManager()
    ip = ipaddress.ip_address('192.0.2.1') 
    team_manager.register(ip,"team1")
    print(team_manager.get_team_name(ip))
    team_manager.register(ipaddress.ip_address('192.0.2.2'), "team2")
    print(team_manager.get_registered_teams())
    print(team_manager.get_free_teams())
    team_manager.allocate(ip, 1)
    time.sleep(TIMEOUT)
    print(team_manager.get_timed_out_teams())
    team_manager.deallocate(ip)
