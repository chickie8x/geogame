import threading
import time
import random

class LeaderElection:
    def __init__(self, num_participants):
        self.num_participants = num_participants
        self.identifiers = [random.randint(1, 100) for _ in range(num_participants)]
        self.leader = None
        self.election_lock = threading.Lock()

    def start_election(self):
        with self.election_lock:
            for i in range(self.num_participants):
                participant_id = self.identifiers[i]
                right_neighbor_id = self.identifiers[(i + 1) % self.num_participants]

                if self.leader is None or participant_id > self.leader:
                    if participant_id > right_neighbor_id:
                        self.leader = participant_id

            print(f"Leader elected: Participant {self.identifiers.index(self.leader)} with ID {self.leader}")

# Simulating the Leader Election
num_participants = 5
election = LeaderElection(num_participants)

# Simulate multiple leader elections
for round_num in range(3):
    print(f"\nLeader Election Round {round_num + 1}:\n")
    election.start_election()
    time.sleep(2)  # Pause between leader elections
