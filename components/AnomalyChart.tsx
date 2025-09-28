"use client"
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceDot } from "recharts"

export default function AnomalyChart({ data }: { data: any[] }) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="temp" stroke="#8884d8" strokeWidth={2} dot={false} />
          {data.map((d) =>
            d.anomaly ? <ReferenceDot key={d.year} x={d.year} y={d.temp} r={5} stroke="red" fill="red" /> : null
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
