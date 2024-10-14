import {formatNumberShort} from "../utils";

describe('formatNumberShort', () => {
  test('handles null and undefined', () => {
    expect(formatNumberShort(null)).toBe('N/A');
    expect(formatNumberShort(undefined)).toBe('N/A');
  });

  test('formats billions correctly', () => {
    expect(formatNumberShort(1000000000)).toBe('1B');
    expect(formatNumberShort(1500000000)).toBe('1.5B');
  });

  test('formats millions correctly', () => {
    expect(formatNumberShort(1000000)).toBe('1M');
    expect(formatNumberShort(1500000)).toBe('1.5M');
  });

  test('formats thousands correctly', () => {
    expect(formatNumberShort(1000)).toBe('1k');
    expect(formatNumberShort(1500)).toBe('1.5k');
  });

  test('formats numbers less than 10 correctly', () => {
    expect(formatNumberShort(1.93)).toBe('1.93');
    expect(formatNumberShort(5.67)).toBe('5.67');
    expect(formatNumberShort(0.01)).toBe('0.01');
    expect(formatNumberShort(1.09)).toBe('1.09');
    expect(formatNumberShort(1.0000019)).toBe('1');
  });

  test('formats numbers between 10 and 99 correctly', () => {
    expect(formatNumberShort(10.5)).toBe('10.5');
    expect(formatNumberShort(99.9)).toBe('99.9');
  });

  test('formats numbers 100 and above correctly', () => {
    expect(formatNumberShort(100)).toBe('100');
    expect(formatNumberShort(999)).toBe('999');
  });

  test('removes trailing zeros', () => {
    expect(formatNumberShort(1.00)).toBe('1');
    expect(formatNumberShort(10.0)).toBe('10');
  });
});
