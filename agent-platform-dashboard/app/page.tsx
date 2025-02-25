"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AgentsOnline } from "@/components/agents-online";
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart2, Award } from "lucide-react";

const metrics = [
  { title: "Total Agents Running", value: "42", icon: Activity, trend: "up" },
  { title: "Total Trades Executed", value: "1,234", icon: BarChart2, trend: "up" },
  { title: "Average ROI", value: "8.7%", icon: TrendingUp, trend: "up" },
  { title: "Average Sharpe Ratio", value: "1.2", icon: Award, trend: "down" },
  { title: "Total Wins", value: "876", icon: TrendingUp, trend: "up" },
  { title: "Total Losses", value: "358", icon: TrendingDown, trend: "down" },
];

export default function Dashboard() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch("/api/agent");
        if (!response.ok) throw new Error("Failed to fetch agents.");
        const data = await response.json();
        setAgents(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error occurred.");
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
              <metric.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className="text-xs text-muted-foreground">
                {metric.trend === "up" ? (
                  <TrendingUp className="inline h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="inline h-4 w-4 text-red-500" />
                )}{" "}
                {metric.trend === "up" ? "Increase" : "Decrease"} from last period
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Agents Online</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Pass agents and error states as props */}
          <AgentsOnline agents={agents} loading={loading} error={error} />
        </CardContent>
      </Card>
    </div>
  );
}
