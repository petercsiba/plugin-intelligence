# https://chatgpt.com/c/c2d0f3da-4d17-4cc5-8fbc-ddca340842dc
import matplotlib.pyplot as plt
import pandas as pd

# Data
data = {
    "range": [
        "0-10", "11-100", "101-1000", "1001-10000",
        "10001-100000", "100001-1000000",
        "1000001-10000000", "10000001-100000000",
        "100000001-1000000000"
    ],
    "count": [
        29476, 30959, 31510, 11847, 4043, 1106, 231, 27, 1
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Modify the range labels for better readability
readable_ranges = [
    "0-10", "11-100", "101-1K", "1K+", "10K+", "100K+", "1M+", "10M+", "100M+"
]
df['readable_range'] = readable_ranges

# Plot the histogram with log scale on Y axis, human-readable labels, capped at 100K, and fewer horizontal lines
plt.figure(figsize=(12, 6))
bars = plt.bar(df['readable_range'], df['count'], color='skyblue')
plt.yscale('log')

# Customize the y-axis to have human-readable labels, capped at 100K
plt.yticks([1, 10, 100, 1000, 10000, 100000],
           ['1', '10', '100', '1K', '10K', '100K'])

# Add horizontal lines for better readability, with fewer lines
plt.grid(axis='y', which='major', linestyle='--', linewidth=0.7)

# Add the absolute numbers on top of each histogram bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{int(height)}', ha='center', va='bottom', fontsize=10)

plt.xlabel('User Count Range')
plt.ylabel('Count (Log Scale)')
plt.title('Histogram of User Count Ranges (Log Scale, Capped at 100K)')
plt.xticks(rotation=45)

# Save and display the histogram
plt.tight_layout()
plt.savefig('user_count_histogram_log_scale_fewer_lines.png')
plt.show()