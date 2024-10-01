import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

# Sample data (replace these with your actual lists)
gains = [48858.0, -12915.0, -13521.0, 210580.0, -16332.0, -3556.0, -30354.0, -27472.0, -24342.0, -11647.0, -23178.0, -14960.0, -22854.0, 621.0, -14115.0, 116429.0, -25629.0, 955534.0, 783237.0, -245452.0, 4267611.0, 2843090.0, 4171356.0, -1091154.0, -1178846.0, 696718.0]
durations = [324.0, 40.0, 37.0, 715.0, 153.0, 103.0, 18.0, 45.0, 28.0, 183.0, 26.0, 127.0, 12.0, 400.0, 8.0, 951.0, 134.0, 1137.0, 577.0, 154.0, 1318.0, 698.0, 834.0, 43.0, 38.0, 372.0]

# Create bell curve for gains
plt.figure(figsize=(14, 6))

# Histogram for gains
plt.subplot(1, 2, 1)
sns.histplot(gains, bins=10, kde=False, color='skyblue', stat='density')
mean_gains = np.mean(gains)
std_gains = np.std(gains)
xmin, xmax = plt.xlim()  # Get x limits for plotting the bell curve
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mean_gains, std_gains)  # Calculate the normal distribution
plt.plot(x, p, 'k', linewidth=2, label='Bell Curve')
plt.title('Distribution of Gains ($)')
plt.xlabel('Gains ($)')
plt.ylabel('Density')
plt.legend()

# Histogram for trade durations
plt.subplot(1, 2, 2)
sns.histplot(durations, bins=10, kde=False, color='lightgreen', stat='density')
mean_durations = np.mean(durations)
std_durations = np.std(durations)
xmin, xmax = plt.xlim()  # Get x limits for plotting the bell curve
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mean_durations, std_durations)  # Calculate the normal distribution
plt.plot(x, p, 'k', linewidth=2, label='Bell Curve')
plt.title('Distribution of Trade Durations (Days)')
plt.xlabel('Duration (Days)')
plt.ylabel('Density')
plt.legend()

plt.tight_layout()
plt.show()