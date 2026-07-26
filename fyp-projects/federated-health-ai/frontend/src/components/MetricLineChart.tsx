import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface ChartSeries {
  key: string;
  label: string;
  color: string;
}

export interface MetricLineChartProps {
  data: object[];
  xKey: string;
  xLabel?: string;
  series: ChartSeries[];
  yDomain?: [number | "auto", number | "auto"];
  yFormatter?: (value: number) => string;
}

const TICK_STYLE = { fill: "#898781", fontSize: 11 };
const TOOLTIP_STYLE = {
  backgroundColor: "#222221",
  border: "1px solid rgba(255,255,255,0.18)",
  borderRadius: 8,
  fontSize: 12,
  color: "#ffffff",
};

export function MetricLineChart({
  data,
  xKey,
  xLabel,
  series,
  yDomain,
  yFormatter,
}: MetricLineChartProps) {
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 8, right: 12, bottom: xLabel ? 18 : 4, left: 0 }}
        >
          <CartesianGrid stroke="#2c2c2a" vertical={false} />
          <XAxis
            dataKey={xKey}
            tick={TICK_STYLE}
            stroke="#383835"
            tickLine={false}
            label={
              xLabel
                ? {
                    value: xLabel,
                    position: "insideBottom",
                    offset: -12,
                    fill: "#898781",
                    fontSize: 11,
                  }
                : undefined
            }
          />
          <YAxis
            tick={TICK_STYLE}
            stroke="#383835"
            tickLine={false}
            width={48}
            domain={yDomain}
            tickFormatter={yFormatter}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            labelStyle={{ color: "#c3c2b7" }}
            formatter={(value: number | string) =>
              typeof value === "number" ? value.toFixed(4) : value
            }
            labelFormatter={(label) =>
              xLabel ? `${xLabel} ${String(label)}` : String(label)
            }
          />
          {series.length > 1 && (
            <Legend
              wrapperStyle={{ fontSize: 12, color: "#c3c2b7" }}
              iconType="plainline"
            />
          )}
          {series.map((s) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              name={s.label}
              stroke={s.color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/** Categorical slots from the validated dark-mode palette. */
export const CHART_COLORS = {
  accuracy: "#3987e5",
  auc: "#199e70",
  loss: "#d95926",
};
