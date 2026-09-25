import { describe, expect, it } from "vitest";

import { formatCOP, formatFecha, formatMillonesCOP } from "./format";

describe("formatCOP", () => {
  it("formats whole pesos below 1.000 millones", () => {
    expect(formatCOP(450_000_000)).toBe("COP 450.000.000");
  });

  it("formats whole millones at or above 1.000 millones", () => {
    expect(formatCOP(32_000_000_000)).toBe("COP 32.000 millones");
  });

  it("formats zero as COP 0", () => {
    expect(formatCOP(0)).toBe("COP 0");
  });

  it("rounds half away from zero", () => {
    expect(formatCOP(1_234.6)).toBe("COP 1.235");
  });

  it("formats a large amount in millones, rounded", () => {
    expect(formatCOP(1_234_567_890_123)).toBe("COP 1.234.568 millones");
  });

  it("chooses the display form after rounding to whole pesos (just below threshold)", () => {
    expect(formatCOP(999_999_999.4)).toBe("COP 999.999.999");
  });

  it("chooses the display form after rounding to whole pesos (just at threshold)", () => {
    expect(formatCOP(999_999_999.6)).toBe("COP 1.000 millones");
  });

  it("formats exactly 1.000 millones", () => {
    expect(formatCOP(1_000_000_000)).toBe("COP 1.000 millones");
  });

  it("throws on negative input", () => {
    expect(() => formatCOP(-1)).toThrow();
  });

  it("throws on NaN", () => {
    expect(() => formatCOP(Number.NaN)).toThrow();
  });

  it("throws on non-finite input", () => {
    expect(() => formatCOP(Number.POSITIVE_INFINITY)).toThrow();
  });

  it("never abbreviates as a standalone M", () => {
    expect(formatCOP(32_000_000_000)).not.toMatch(/\bM\b/);
    expect(formatCOP(450_000_000)).not.toMatch(/\bM\b/);
  });
});

describe("formatMillonesCOP", () => {
  it("formats a large amount", () => {
    expect(formatMillonesCOP(32_000_000_000)).toBe("32.000");
  });

  it("formats an exact millones amount", () => {
    expect(formatMillonesCOP(450_000_000)).toBe("450");
  });

  it("rounds half away from zero", () => {
    expect(formatMillonesCOP(1_500_000)).toBe("2");
  });

  it("formats zero as 0", () => {
    expect(formatMillonesCOP(0)).toBe("0");
  });

  it("shows < 1 for amounts that round down to zero millones", () => {
    expect(formatMillonesCOP(499_999)).toBe("< 1");
  });

  it("shows the rounded value once it reaches the half-millon boundary", () => {
    expect(formatMillonesCOP(500_000)).toBe("1");
  });

  it("throws on negative input", () => {
    expect(() => formatMillonesCOP(-1)).toThrow();
  });

  it("throws on NaN", () => {
    expect(() => formatMillonesCOP(Number.NaN)).toThrow();
  });

  it("throws on non-finite input", () => {
    expect(() => formatMillonesCOP(Number.POSITIVE_INFINITY)).toThrow();
  });

  it("never abbreviates as a standalone M", () => {
    expect(formatMillonesCOP(32_000_000_000)).not.toMatch(/\bM\b/);
  });
});

describe("formatFecha", () => {
  it("formats a calendar date as dd-mm-aaaa", () => {
    expect(formatFecha("2024-03-07")).toBe("07-03-2024");
  });

  it("throws on a timestamp", () => {
    expect(() => formatFecha("2024-03-07T00:00:00Z")).toThrow();
  });

  it("throws on an impossible calendar date", () => {
    expect(() => formatFecha("2024-02-30")).toThrow();
  });

  it("throws on a month below 1", () => {
    expect(() => formatFecha("2024-00-01")).toThrow();
  });

  it("throws on a month above 12", () => {
    expect(() => formatFecha("2024-13-01")).toThrow();
  });

  it("accepts February 29 in a leap year", () => {
    expect(formatFecha("2024-02-29")).toBe("29-02-2024");
  });

  it("throws on February 29 in a non-leap year", () => {
    expect(() => formatFecha("2023-02-29")).toThrow();
  });

  it("throws on garbage input", () => {
    expect(() => formatFecha("not-a-date")).toThrow();
  });
});
