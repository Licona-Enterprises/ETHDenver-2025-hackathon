"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AgentDetailView } from "@/components/agent-detail-view"

interface Agent {
  _id: string
  agentName: string
  strategyType: string
}

interface TokenDetail {
  symbol: string
  token_address: string
  token_id: number
  amount: number
  signal_price: number
  signal_timestamp: string
  last_price: number
}

interface PortfolioMetric {
  symbol: string
  signal_price: number
  last_price: number
  token_amount: number
  PnL: number
  cumulative_return: number
  daily_return: number
  volatility: number
  sharpe_ratio: number
  max_drawdown: number
  holding_duration_days: number
}

interface Portfolio {
  _id: string
  agentId: string
  portfolioDetails: Record<string, TokenDetail> // BTC, ETH, etc.
  portfolioMetrics: PortfolioMetric[]
}

export default function MyAgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)

  useEffect(() => {
    async function fetchAgents() {
      try {
        const response = await fetch("/api/agent")
        if (!response.ok) throw new Error("Failed to fetch agents")
        const data: Agent[] = await response.json()
        setAgents(data)
      } catch (error) {
        console.error("Error fetching agents:", error)
      }
    }

    fetchAgents()
  }, [])

  useEffect(() => {
    async function fetchPortfolio() {
      if (!selectedAgent) return

      try {
        const response = await fetch(`/api/agent-portfolio?agentId=${selectedAgent}`)
        if (!response.ok) throw new Error("Failed to fetch portfolio")
        const data: Portfolio = await response.json()
        setPortfolio(data)
      } catch (error) {
        console.error("Error fetching portfolio:", error)
        setPortfolio(null)
      }
    }

    fetchPortfolio()
  }, [selectedAgent])

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">My Agents</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <Card key={agent._id} className="cursor-pointer" onClick={() => setSelectedAgent(agent._id)}>
            <CardHeader>
              <CardTitle>{agent.agentName}</CardTitle>
              <CardDescription>
                {/* <Badge variant="success">Online</Badge>  */}
                <Badge>Online</Badge>
              </CardDescription>
            </CardHeader>
            {/* <CardContent>
              <p>Strategy: {agent.strategyType}</p>
            </CardContent> */}
          </Card>
        ))}
      </div>

      {selectedAgent && portfolio && (
        <AgentDetailView agentId={selectedAgent} portfolio={portfolio} onClose={() => setSelectedAgent(null)} />
      )}
    </div>
  )
}
