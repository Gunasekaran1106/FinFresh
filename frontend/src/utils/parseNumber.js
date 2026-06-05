/**
 * Safe number parsing utility.
 * Handles strings, numbers, null, undefined, and invalid inputs.
 * Returns 0 for any invalid value.
 */
export const parseNumber = (value) => {
  if (value === null || value === undefined) {
    return 0;
  }

  const num = Number(value);
  return isNaN(num) ? 0 : num;
};
