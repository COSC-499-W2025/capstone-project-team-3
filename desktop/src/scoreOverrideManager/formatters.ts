export function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function scoreColor(value: number): string {
  if (value >= 0.75) return "#27ae60";
  if (value >= 0.5) return "#f39c12";
  return "#e74c3c";
}
