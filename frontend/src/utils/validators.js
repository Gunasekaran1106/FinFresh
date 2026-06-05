/**
 * Validation utilities for frontend.
 */

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  if (password.length < 8) return "Password must be at least 8 characters";
  if (!/[A-Z]/.test(password)) return "Password must contain at least one uppercase letter";
  if (!/[0-9]/.test(password)) return "Password must contain at least one digit";
  return null;
};

export const validateName = (name) => {
  if (!name.trim()) return "Name is required";
  if (name.length < 2) return "Name must be at least 2 characters";
  return null;
};
