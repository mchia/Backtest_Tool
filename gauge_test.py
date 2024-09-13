import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# Define the range of values and create a colormap
values: list[int] = [0, 10, 20, 30, 40]  # Example values
labels: list[str] = ["Strong Buy", "Buy", "Neutral", "Sell", "Strong Sell"]
cmap = plt.get_cmap('RdYlGn')  # Red to Yellow to Green colormap
norm = mcolors.Normalize(vmin=min(values), vmax=max(values))

# Angular positions for 5 segments
x_radians = np.linspace(0, np.pi, len(values), endpoint=False)  # 180 degrees
width: float = np.pi / len(values)  # Width of each segment

# Create figure and polar axis
fig = plt.figure(figsize=(18, 18))
ax = fig.add_subplot(projection="polar")

# Plot bars on the polar axis with colors based on the values
bars = ax.bar(
    x=x_radians,
    width=width,
    height=[0.2]*5,  # Uniform height for each segment
    bottom=[2]*5,    # Uniform bottom for each segment
    color=[cmap(norm(val)) for val in values],
    align="edge"
)

# for i, (label, loc) in enumerate(zip(labels, x_radians)):
#     plt.annotate(label, xy=(loc + width / 2, 2.1), rotation=-30 + i * 15, color="white", fontweight="bold")

# Add value annotations
for loc, val in zip(x_radians, values):
    plt.annotate(val, xy=(loc + width / 2, 2.5), ha="center", color="black")

# Add a special annotation for the center
plt.annotate("50", xytext=(0, 0), xy=(np.pi / 2, 2.0),
    arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
    bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0),
    fontsize=45, color="white", ha="center"
)

# Add title and configure plot
plt.title("Performance Gauge Chart", loc="center", pad=20, fontsize=35, fontweight="bold")
ax.set_axis_off()

# Show plot
plt.show()