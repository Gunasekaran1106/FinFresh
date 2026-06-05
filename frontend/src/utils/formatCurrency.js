/**
 * Format a number as Indian Rupee currency.
 * Uses INR locale and hides decimal places for whole amounts.
 */
export const formatCurrency = (value) => {
  const num = Number(value) || 0;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(num);
};

/**
 * Format a date string to DD-MM-YYYY format.
 */
export const formatDate = (dateString) => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN");
  } catch {
    return dateString;
  }
};
