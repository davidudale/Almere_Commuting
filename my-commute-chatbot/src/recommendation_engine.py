# src/recommendation_engine.py

import pandas as pd
import os

def load_commuter_data(filepath="data/commuter_data.csv"):
    """Loads the commuter dataset."""
    if not os.path.exists(filepath):
        print(f"Error: Data file not found at {filepath}")
        return pd.DataFrame() # Return empty DataFrame
    return pd.read_csv(filepath)

def get_commuter_profile(commuter_id, df):
    """Retrieves a specific commuter's TPB profile."""
    profile = df[df['CommuterID'] == commuter_id].iloc[0]
    return profile.to_dict()

def generate_recommendations(user_profile, crowding_insights=None):
    """
    Generates personalized commuting recommendations based on the user's TPB profile
    and optional crowding insights.
    """
    recommendations = []

    # --- General TPB-based recommendations ---

    # Public Transport (PT)
    if user_profile['Intention_PT_Score'] < 4: # Low intention for PT
        if user_profile['Attitude_PT_Score'] < 4: # Negative attitude towards PT
            recommendations.append(
                "It seems you have a negative attitude towards public transport. "
                "Consider exploring its potential benefits, such as reducing stress from driving, "
                "saving on fuel/parking costs, or the opportunity to relax/work during commute. "
                "Perhaps try a short trip during off-peak hours to experience it."
            )
        if user_profile['SN_PT_Score'] < 4: # Low subjective norm for PT
            recommendations.append(
                "Your social circle might not strongly influence you to use public transport. "
                "Talk to colleagues or friends who use PT; they might share positive experiences or tips "
                "that could change your perception."
            )
        if user_profile['PBC_PT_Score'] < 4: # Low perceived behavioral control for PT
            recommendations.append(
                "You seem to perceive challenges with using public transport. "
                "Try researching routes and schedules using apps (e.g., Google Maps, local transit apps). "
                "Understanding the system better can greatly improve your perceived ease of use. "
                "Perhaps a trial run on a non-work day could help build confidence."
            )
    elif user_profile['Intention_PT_Score'] >= 5: # High intention for PT
        recommendations.append(
            "You have a strong intention to use public transport, which is great! "
            "Keep leveraging its benefits for a sustainable and potentially less stressful commute."
        )

    # Car
    if user_profile['Intention_Car_Score'] >= 5: # High intention for Car
        if user_profile['Attitude_Car_Score'] >= 5 and user_profile['PBC_Car_Score'] >= 5:
             recommendations.append(
                "You seem to strongly prefer using a car due to high perceived control and positive attitude. "
                "If congestion is a concern, consider carpooling or adjusting your commute time."
            )
        if user_profile['SN_Car_Score'] < 4: # Low subjective norm for Car (e.g., social pressure to be green)
            recommendations.append(
                "While you might prefer driving, consider the environmental or community impact. "
                "Exploring alternatives, even occasionally, could align with broader social trends."
            )


    # Walk/Cycle
    if user_profile['Intention_WalkCycle_Score'] >= 5: # High intention for Walk/Cycle
        if user_profile['PBC_WalkCycle_Score'] < 4: # Low perceived control for Walk/Cycle
            recommendations.append(
                "You intend to walk or cycle, but might face challenges. "
                "Check for safe bike lanes or pedestrian paths. "
                "Even partial walking/cycling (e.g., to the nearest PT stop) can be beneficial."
            )
        else:
            recommendations.append(
                "Great! You have a high intention and perceived control for walking or cycling. "
                "This is an excellent option for health and environment. Keep it up!"
            )

    # --- Crowding-specific recommendations (from simulation insights) ---
    if crowding_insights:
        avg_crowding = crowding_insights.get("average_pt_crowding", 0)
        total_switches = crowding_insights.get("total_mode_switches_from_pt", 0)

        if avg_crowding > 0.7: # High crowding threshold
            recommendations.append(
                f"**Crowding Alert:** Our simulation indicates public transport can be quite crowded (average crowding: {avg_crowding:.0%}). "
                "If you're sensitive to crowding, consider adjusting your commute time to off-peak hours, "
                "or exploring alternative routes/modes on particularly busy days."
            )
        elif avg_crowding > 0.4: # Moderate crowding
            recommendations.append(
                f"Our simulation shows moderate public transport crowding (average crowding: {avg_crowding:.0%}). "
                "While not extremely high, being aware of peak times can help you plan a more comfortable journey."
            )
        else: # Low crowding
            recommendations.append(
                f"Our simulation suggests public transport is generally not overly crowded (average crowding: {avg_crowding:.0%}). "
                "This might be a good time to try it if crowding was a concern."
            )

        if total_switches > 0 and user_profile['UsualCommuteMode'] == "Public Transport":
            recommendations.append(
                f"Our simulation also observed {total_switches} instances of commuters switching away from public transport due to crowding. "
                "This highlights the importance of checking real-time conditions if PT is your preferred mode."
            )

    if not recommendations:
        recommendations.append(
            "Based on your profile, you seem to have a balanced view on commuting. "
            "Consider your daily needs and external factors like weather or traffic when choosing your mode."
        )

    return recommendations

# Example usage (for testing this module directly)
if __name__ == "__main__":
    # Ensure you have a 'data' folder with 'commuter_data.csv' for this to run
    # You might need to adjust the path if running from a different directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_filepath = os.path.join(current_dir, '..', 'data', 'commuter_data.csv')

    commuter_df = load_commuter_data(data_filepath)

    if not commuter_df.empty:
        # Test with CommuterID 102 (Public Transport user, moderate scores)
        profile_102 = get_commuter_profile(102, commuter_df)
        print(f"--- Recommendations for CommuterID 102 (Usual Mode: {profile_102['UsualCommuteMode']}) ---")
        recs_102 = generate_recommendations(profile_102, crowding_insights={"average_pt_crowding": 0.85, "total_mode_switches_from_pt": 15})
        for rec in recs_102:
            print(f"- {rec}")

        # Test with CommuterID 101 (Car user, high scores)
        profile_101 = get_commuter_profile(101, commuter_df)
        print(f"\n--- Recommendations for CommuterID 101 (Usual Mode: {profile_101['UsualCommuteMode']}) ---")
        recs_101 = generate_recommendations(profile_101, crowding_insights={"average_pt_crowding": 0.3, "total_mode_switches_from_pt": 2})
        for rec in recs_101:
            print(f"- {rec}")

        # Test with CommuterID 103 (Walk/Cycle user, low PT/Car scores)
        profile_103 = get_commuter_profile(103, commuter_df)
        print(f"\n--- Recommendations for CommuterID 103 (Usual Mode: {profile_103['UsualCommuteMode']}) ---")
        recs_103 = generate_recommendations(profile_103, crowding_insights={"average_pt_crowding": 0.6, "total_mode_switches_from_pt": 8})
        for rec in recs_103:
            print(f"- {rec}")
    else:
        print("Could not load commuter data for testing.")
