# https://chatgpt.com/c/c2d0f3da-4d17-4cc5-8fbc-ddca340842dc
import matplotlib.pyplot as plt
import pandas as pd

# Data
# SELECT
#     CASE
#         WHEN user_count IS NULL OR (user_count BETWEEN 0 AND 10) THEN '0-10'
#         WHEN user_count BETWEEN 11 AND 100 THEN '11-100'
#         WHEN user_count BETWEEN 101 AND 1000 THEN '101-1000'
#         WHEN user_count BETWEEN 1001 AND 10000 THEN '1001-10000'
#         WHEN user_count BETWEEN 10001 AND 100000 THEN '10001-100000'
#         WHEN user_count BETWEEN 100001 AND 1000000 THEN '100001-1000000'
#         WHEN user_count BETWEEN 1000001 AND 10000000 THEN '1000001-10000000'
#         WHEN user_count BETWEEN 10000001 AND 100000000 THEN '10000001-100000000'
#         WHEN user_count BETWEEN 100000001 AND 1000000000 THEN '100000001-1000000000'
#         ELSE '1000000001+'
#     END AS range,
#     COUNT(*) AS count
# FROM google_workspace
# WHERE p_date = '2024-05-16'
# GROUP BY range
# ORDER BY MIN(user_count);

google_workspace_data = {
    "range": [
        "0-10", "11-100", "101-1000", "1001-10000",
        "10001-100000", "100001-1000000",
        "1000001-10000000", "10000001-100000000",
        "100000001-1000000000"
    ],
    "count": [
        84, 445, 1200, 889, 1078, 892, 157, 117, 1
    ]
}
chrome_extension_data = {
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
df = pd.DataFrame(chrome_extension_data)

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
# plt.yticks([1, 10, 100, 1000, 10000, 100000],
#            ['1', '10', '100', '1K', '10K', '100K'])
# Customize the y-axis to have human-readable labels, capped at 100K
plt.yticks([1, 10, 100, 1000, 10000],
           ['1', '10', '100', '1K', '10K'])

# Add horizontal lines for better readability, with fewer lines
plt.grid(axis='y', which='major', linestyle='--', linewidth=0.7)

# Add the absolute numbers on top of each histogram bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{int(height)}', ha='center', va='bottom', fontsize=10)

plt.xlabel('Downloads Count Range')
plt.ylabel('Plugin Count (Log Scale)')
plt.title('Histogram of Downloads Count Ranges (Log Scale)')
plt.xticks(rotation=45)

# Save and display the histogram
plt.tight_layout()
plt.savefig('downloads_count_histogram_log_scale_fewer_lines.png')
plt.show()
