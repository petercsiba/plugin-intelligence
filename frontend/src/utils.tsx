// For some super-weird reason, the Python FastAPI server converts my None values into [null] in JSON
// No idea why, spent almost an hour of my life just that I can write this hacky function.
// OMG FACEPALM, somehow the code reformatted to add (value, ) so everything was a tuple :/ Likely copy-pasta.
// WELL, I guess this function ain't needed anymore, but I'll keep it here for posterity.
export function fixThatArrayWithNullShit<T>(input: T | null | undefined | Array<T | null | undefined>): T | null | undefined {
  // Check if the input is null or undefined
  if (input === null || input === undefined) {
    return input;
  }

  // Check if the input is an array
  if (Array.isArray(input)) {
    // Check if the array has exactly one element
    if (input.length === 1) {
      // Return the single element
      return input[0];
    }
  }

  // If it's not an array with exactly one element, return the input as is
  // @ts-ignore
  return input;
}

/**
 * Function to pretty-print monetary values with suffixes (k, M, etc.)
 * @param value - The monetary value to format
 * @returns Formatted string representing the value with the appropriate suffix
 */
export function formatCurrency(value: number | null | undefined): string {
  if (value == null) {
    return 'N/A';
  }
  return `$${formatNumberShort(value)}`;
}

function debugError(error: unknown): void {
  if (error instanceof Error) {
    console.error('An error occurred:', error.message);
    console.error('Call stack:', error.stack);
  } else {
    // Log the error as an unknown type
    console.error('An unexpected type of error occurred:', error);
  }
}

// Mostly for INT values over 1000
export function formatNumberShort(value: number | null | undefined): string {
  if (value == null) {
    return 'N/A';
  }

  // Define suffixes and their thresholds
  const suffixes = [
    { threshold: 1e9, suffix: "B" }, // Billions
    { threshold: 1e6, suffix: "M" }, // Millions
    { threshold: 1e3, suffix: "k" }, // Thousands
  ];

  // Helper function to remove trailing zeros and unnecessary decimal point
  function cleanNumber(numStr: string): string {
    return numStr.replace(/\.0+$/, '');
  }

  // Loop through the suffixes to find an appropriate threshold
  for (const { threshold, suffix } of suffixes) {
    if (Math.abs(value) >= threshold) {
      return `${cleanNumber((value / threshold).toFixed(1))}${suffix}`;
    }
  }

  // Format without suffix if below the thousands threshold
  if (Math.abs(value) < 10) {
    return cleanNumber(value.toFixed(2)); // 2 decimal places for values less than 10
  } else if (Math.abs(value) < 100) {
    return cleanNumber(value.toFixed(1)); // 1 decimal place for values between 10 and 99
  } else {
    return cleanNumber(value.toFixed(0)); // 0 decimal places for values 100 and above
  }
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) {
    return 'N/A';
  }
  // Use Intl.NumberFormat to format the number with thousands separators and a maximum of two decimal places
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value);
}
