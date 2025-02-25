"use client";

import { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface Agent {
  _id: string;
  agentName: string;
  strategyType: string;
  startingPortfolio: number;
  maxTradeFrequency: number;
  tokenPreference: string[];
  persona: string;
  knowledgeBase: string;
}

interface AgentsOnlineProps {
  agents: Agent[];
  loading: boolean;
  error: string;
}

export function AgentsOnline({ agents, loading, error }: AgentsOnlineProps) {
  const [filter, setFilter] = useState("");

  const filteredAgents = agents.filter((agent) =>
    agent.agentName.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) return <p>Loading agents...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="space-y-4">
      <Input
        placeholder="Search agents..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Agent Name</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Trades Executed</TableHead>
            <TableHead>ROI</TableHead>
            <TableHead>Last Activity</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredAgents.map((agent) => (
            <TableRow key={agent._id}>
              <TableCell className="font-medium">{agent.agentName}</TableCell>
              <TableCell>
                <Badge>Online</Badge> {/* Static badge */}
              </TableCell>
              <TableCell>0</TableCell> {/* Placeholder */}
              <TableCell>0%</TableCell> {/* Placeholder */}
              <TableCell>0 min ago</TableCell> {/* Placeholder */}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );

}