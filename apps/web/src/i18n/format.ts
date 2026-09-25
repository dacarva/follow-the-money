const MILLONES_THRESHOLD_PESOS = 1_000_000_000;
const PESOS_PER_MILLON = 1_000_000;

function validateAmount(value: number): void {
  if (Number.isNaN(value) || !Number.isFinite(value)) {
    throw new RangeError("amount must be a finite number");
  }
  if (value < 0) {
    throw new RangeError("amount must not be negative");
  }
}

function formatEsCoInteger(locale: string, value: number): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(
    value,
  );
}

/**
 * Formats a peso amount (the API's raw value) as "COP <pesos>" below 1.000
 * millones, or "COP <millones> millones" at or above it. Never "M".
 */
export function formatCOP(value: number, locale = "es-CO"): string {
  validateAmount(value);
  const roundedPesos = Math.round(value);
  if (roundedPesos < MILLONES_THRESHOLD_PESOS) {
    return `COP ${formatEsCoInteger(locale, roundedPesos)}`;
  }
  const millones = Math.round(roundedPesos / PESOS_PER_MILLON);
  return `COP ${formatEsCoInteger(locale, millones)} millones`;
}

/**
 * Formats a peso amount as a plain number of whole millones for table
 * cells, e.g. for the "Millones COP" column.
 */
export function formatMillonesCOP(value: number, locale = "es-CO"): string {
  validateAmount(value);
  if (value === 0) {
    return formatEsCoInteger(locale, 0);
  }
  const millones = Math.round(value / PESOS_PER_MILLON);
  if (millones === 0) {
    return "< 1";
  }
  return formatEsCoInteger(locale, millones);
}

const DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;

function daysInMonth(year: number, month: number): number {
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

/**
 * Formats a calendar date `YYYY-MM-DD` (no time, no time-zone conversion)
 * as `dd-mm-aaaa`. Throws on anything else, including timestamps and
 * impossible calendar dates.
 */
export function formatFecha(iso: string): string {
  const match = DATE_RE.exec(iso);
  if (!match) {
    throw new RangeError(`formatFecha: expected YYYY-MM-DD, got "${iso}"`);
  }
  const [, yearStr, monthStr, dayStr] = match;
  const year = Number(yearStr);
  const month = Number(monthStr);
  const day = Number(dayStr);
  if (month < 1 || month > 12 || day < 1 || day > daysInMonth(year, month)) {
    throw new RangeError(`formatFecha: invalid calendar date "${iso}"`);
  }
  return `${dayStr}-${monthStr}-${yearStr}`;
}
