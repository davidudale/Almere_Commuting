# src/agent_simulation.py

import random
import pandas as pd

class CommuterAgent:
    """
    Represents a single commuter agent in the simulation.
    Includes TPB attributes and a simple crowding tolerance.
    """
    def __init__(self, id, usual_mode, attitude_pt, pbc_pt, crowding_tolerance=None):
        self.id = id
        self.usual_mode = usual_mode
        self.current_mode = usual_mode
        self.attitude_pt = attitude_pt # Attitude towards Public Transport
        self.pbc_pt = pbc_pt         # Perceived Behavioral Control for Public Transport
        # Individual tolerance to crowding (0-1, lower means less tolerant)
        self.crowding_tolerance = crowding_tolerance if crowding_tolerance is not None else random.uniform(0.5, 0.9)

    def decide_on_pt(self, perceived_crowding_level):
        """
        Agent decides whether to use PT based on perceived crowding and TPB scores.
        Returns True if they stick with PT, False if they might switch.
        """
        # If usual mode is not PT, they won't consider PT for crowding response
        if self.usual_mode != "Public Transport":
            return False # They are not initially on PT, so crowding won't make them switch *from* PT

        # Adjust perceived PBC/Attitude based on crowding
        # This is a simplification: higher crowding reduces perceived control and attitude
        # The impact of crowding is stronger if the agent's tolerance is exceeded.
        crowding_impact = max(0, perceived_crowding_level - self.crowding_tolerance) * 2 # Scale impact
        
        adjusted_pbc_pt = max(1, self.pbc_pt - (crowding_impact * 3)) # Stronger impact on PBC
        adjusted_attitude_pt = max(1, self.attitude_pt - (crowding_impact * 2)) # Moderate impact on Attitude

        # Simple decision rule: if adjusted scores drop too low, consider switching
        # This can be made more sophisticated with a utility function or probabilistic choice
        if adjusted_pbc_pt < 3 or adjusted_attitude_pt < 3: # Arbitrary threshold for switching
            return False # Agent might switch away from PT
        return True # Agent sticks with PT

class PublicTransportLine:
    """
    Represents a simplified public transport line with a capacity.
    """
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.current_riders = 0

    def get_crowding_level(self):
        """Returns the current crowding level as a ratio (0.0 to 1.0)."""
        if self.capacity == 0:
            return 0.0
        return min(1.0, self.current_riders / self.capacity)

    def add_rider(self):
        self.current_riders += 1

    def remove_rider(self):
        self.current_riders = max(0, self.current_riders - 1)

    def reset_riders(self):
        self.current_riders = 0

def run_crowding_simulation(commuters_df, pt_capacity=100, num_sim_steps=5):
    """
    Runs a simplified agent-based simulation to model crowding responses.
    This simulation is highly simplified for demonstration purposes.
    It simulates how agents might react to perceived crowding on public transport.

    Args:
        commuters_df (pd.DataFrame): DataFrame containing commuter data.
        pt_capacity (int): The total capacity of the public transport system being simulated.
                           A lower capacity will lead to more perceived crowding.
        num_sim_steps (int): Number of simulation steps (e.g., commute cycles).

    Returns:
        dict: A dictionary containing simulation insights, e.g.,
              average crowding, number of mode switches.
    """
    agents = []
    for index, row in commuters_df.iterrows():
        # Only relevant TPB scores for PT crowding response are passed
        agent = CommuterAgent(
            id=row['CommuterID'],
            usual_mode=row['UsualCommuteMode'],
            attitude_pt=row['Attitude_PT_Score'],
            pbc_pt=row['PBC_PT_Score']
        )
        agents.append(agent)

    pt_line = PublicTransportLine(name="Main PT Line", capacity=pt_capacity)

    mode_switches_total = 0
    crowding_levels_over_time = []
    
    # Filter agents who usually use PT for this simulation
    pt_users = [agent for agent in agents if agent.usual_mode == "Public Transport"]
    other_mode_users = [agent for agent in agents if agent.usual_mode != "Public Transport"]

    print(f"--- Running Crowding Simulation (PT Capacity: {pt_capacity}) ---")

    for step in range(num_sim_steps):
        pt_line.reset_riders() # Reset riders for each "commute cycle"

        # Simulate initial PT riders (those who usually take PT)
        # For simplicity, assume all usual PT users attempt to board
        initial_pt_attempt_count = len(pt_users)
        pt_line.current_riders = initial_pt_attempt_count # Initial load

        perceived_crowding = pt_line.get_crowding_level()
        crowding_levels_over_time.append(perceived_crowding)

        print(f"\nStep {step + 1}: Initial PT riders attempting: {initial_pt_attempt_count}, Perceived Crowding: {perceived_crowding:.2f}")

        # Agents who usually use PT react to crowding
        current_pt_riders_after_response = 0
        for agent in pt_users:
            if agent.decide_on_pt(perceived_crowding):
                # Agent sticks with PT
                current_pt_riders_after_response += 1
            else:
                # Agent switches away from PT
                mode_switches_total += 1
                agent.current_mode = "Alternative" # Mark as switched
                # In a real sim, they'd pick a specific alternative
        
        # Update PT riders based on responses
        pt_line.current_riders = current_pt_riders_after_response
        final_crowding_this_step = pt_line.get_crowding_level()
        
        print(f"Step {step + 1}: PT riders after response: {current_pt_riders_after_response}, Final Crowding: {final_crowding_this_step:.2f}")

    avg_crowding = sum(crowding_levels_over_time) / len(crowding_levels_over_time) if crowding_levels_over_time else 0

    print(f"\nSimulation Summary:")
    print(f"Average Public Transport Crowding: {avg_crowding:.2f}")
    print(f"Total Mode Switches from PT due to Crowding: {mode_switches_total}")

    return {
        "average_pt_crowding": avg_crowding,
        "total_mode_switches_from_pt": mode_switches_total,
        "simulated_pt_capacity": pt_capacity,
        "num_sim_steps": num_sim_steps
    }

# Example usage (for testing this module directly)
if __name__ == "__main__":
    # Create a dummy DataFrame for testing
    data = {
        'CommuterID': [1, 2, 3, 4, 5],
        'UsualCommuteMode': ['Public Transport', 'Car', 'Public Transport', 'Public Transport', 'Walk/Cycle'],
        'Attitude_Car_Score': [7, 6, 2, 3, 1],
        'Attitude_PT_Score': [5, 3, 6, 4, 2],
        'Attitude_WalkCycle_Score': [2, 1, 5, 6, 7],
        'SN_Car_Score': [6, 5, 1, 2, 1],
        'SN_PT_Score': [4, 2, 5, 3, 2],
        'SN_WalkCycle_Score': [1, 1, 4, 5, 6],
        'PBC_Car_Score': [7, 6, 3, 4, 2],
        'PBC_PT_Score': [5, 3, 6, 4, 3],
        'PBC_WalkCycle_Score': [2, 1, 5, 6, 7],
        'Intention_Car_Score': [7, 6, 2, 3, 1],
        'Intention_PT_Score': [5, 3, 6, 4, 2],
        'Intention_WalkCycle_Score': [2, 1, 5, 6, 7],
        'Age': [30, 40, 25, 35, 28],
        'Gender': ['Female', 'Male', 'Female', 'Male', 'Female'],
        'HouseholdIncome': ['Medium', 'High', 'Low', 'Medium', 'Low'],
        'CommuteDistanceKM': [10, 15, 5, 8, 3],
        'ActualModeChoice': ['Public Transport', 'Car', 'Public Transport', 'Public Transport', 'Walk/Cycle']
    }
    test_df = pd.DataFrame(data)

    # Run simulation with different capacities to see crowding effects
    print("\n--- Simulation with High PT Capacity ---")
    results_high_capacity = run_crowding_simulation(test_df, pt_capacity=100, num_sim_steps=3)
    print(results_high_capacity)

    print("\n--- Simulation with Low PT Capacity (more crowding) ---")
    results_low_capacity = run_crowding_simulation(test_df, pt_capacity=3, num_sim_steps=3)
    print(results_low_capacity)
