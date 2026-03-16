import React from "react";
import { pct, scoreColor } from "./formatters";

interface ScoreGaugeProps {
  label: string;
  value: number;
  badge?: React.ReactNode;
}

export default function ScoreGauge({ label, value, badge }: ScoreGaugeProps) {
  const color = scoreColor(value);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const dash = circumference * value;

  return (
    <div className="sor-gauge-wrap">
      <svg className="sor-gauge-svg" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} className="sor-gauge-track" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          className="sor-gauge-fill"
          style={{
            stroke: color,
            strokeDasharray: `${dash} ${circumference}`,
          }}
        />
        <text x="60" y="60" className="sor-gauge-text" dy=".35em">
          {pct(value)}
        </text>
      </svg>
      <p className="sor-gauge-label">{label}</p>
      {badge}
    </div>
  );
}
