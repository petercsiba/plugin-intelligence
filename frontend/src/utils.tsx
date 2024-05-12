/**
 * Function to pretty-print monetary values with suffixes (k, M, etc.)
 * @param value - The monetary value to format
 * @returns Formatted string representing the value with the appropriate suffix
 */
export function formatCurrency(value: number): string {
  return `$${formatNumberShort(value)}`;
}

export function formatNumberShort(value: number): string {
  // Define suffixes and their thresholds
  const suffixes = [
    { threshold: 1e9, suffix: "B" }, // Billions
    { threshold: 1e6, suffix: "M" }, // Millions
    { threshold: 1e3, suffix: "k" }, // Thousands
  ];

  // Helper function to remove trailing ".0" if present
  function cleanTrailingZero(numStr: string): string {
    return numStr.replace(/\.0/, '');
  }

  // Loop through the suffixes to find an appropriate threshold
  for (const { threshold, suffix } of suffixes) {
    if (value >= threshold) {
      return `${cleanTrailingZero((value / threshold).toFixed(1))}${suffix}`;
    }
  }

  // Format without suffix if below the thousands threshold
  let formattedValue: string;
  if (value < 10) {
    formattedValue = `${value.toFixed(2)}`; // 2 decimal places for values less than 10
  } else if (value < 100) {
    formattedValue = `${value.toFixed(1)}`; // 1 decimal place for values between 10 and 99
  } else {
    formattedValue = `${value.toFixed(0)}`; // 0 decimal places for values 100 and above
  }

  return cleanTrailingZero(formattedValue);
}
/**
 * Function to format a number with thousands separators
 * @param value - The user count value to format
 * @returns Formatted string representing the user count
 */
export function formatNumber(value: number): string {
  // Use Intl.NumberFormat to format the number with thousands separators
  return new Intl.NumberFormat('en-US').format(value);
}
