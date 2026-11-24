import pandas as pd
import matplotlib.pyplot as plt

slots = pd.read_csv("data/processed/time_demand.csv")

plt.figure(figsize=(9, 5))
plt.bar(slots["time_slot"], slots["passenger_count"])
plt.title("Passenger Demand by Time Slot")
plt.xlabel("Time Slot")
plt.ylabel("Total Passengers")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("docs/demand_by_time_slot.png")
plt.close()

print("Graph saved successfully!")