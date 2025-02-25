"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

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

interface AgentDetailViewProps {
  agentId: string
  portfolio: Portfolio
  onClose: () => void
}

export function AgentDetailView({ agentId, portfolio, onClose }: AgentDetailViewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          Portfolio {portfolio.agentId} Details
          <Button onClick={onClose}>Close</Button>
        </CardTitle>
      </CardHeader>


      <CardContent>


        <div className="space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Overview</CardTitle>
            </CardHeader>
            <CardContent>
              {/* <p>Total Value: </p> */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Token</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Value</TableHead>

                    <TableHead>Profit/Loss</TableHead>
                    <TableHead>Total Return %</TableHead>
                    <TableHead>Daily Return</TableHead>
                    <TableHead>MDD</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {Object.values(portfolio.portfolioDetails).map((holding: TokenDetail) => {
                    const metric = portfolio.portfolioMetrics.find((m) => m.symbol === holding.symbol);
                    return (
                      <TableRow key={holding.token_address}>
                        <TableCell>{holding.symbol}</TableCell>
                        <TableCell>{holding.amount.toFixed(2)}</TableCell>
                        <TableCell>${(holding.last_price * holding.amount).toFixed(2)}</TableCell> {/* Example calculation */}
                        
                        {/* Add PortfolioMetric values if available */}
                        {metric ? (
                          <>
                            <TableCell className={metric.PnL >= 0 ? "text-green-500" : "text-red-500"}>
                              ${metric.PnL.toFixed(2)}
                            </TableCell>

                            <TableCell className={metric.cumulative_return >= 0 ? "text-green-500" : "text-red-500"}>
                              {(metric.cumulative_return * 100).toFixed(2)}%
                            </TableCell>

                            <TableCell className={metric.daily_return >= 0 ? "text-green-500" : "text-red-500"}>
                              {(metric.daily_return * 100).toFixed(3)}%
                            </TableCell>

                            <TableCell className={metric.max_drawdown >= 0 ? "text-green-500" : "text-red-500"}>
                              {metric.max_drawdown > 0 ? "0.000%" : `${(metric.max_drawdown * 100).toFixed(3)}%`}
                            </TableCell>

                            {/* <TableCell>{metric.volatility.toFixed(2)}</TableCell> */}
                          </>
                        ) : (
                          <>
                            <TableCell colSpan={6} className="text-gray-500">No metrics available</TableCell>
                          </>
                        )}
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>



          {/* TODO add portfolio PnL history to the backend and display here */}
          {/* <Card>
            <CardHeader>
              <CardTitle>Performance Chart</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={portfolio.portfolioMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="symbol" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="cumulative_return" stroke="#8884d8" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card> */}



          <Card>
            <CardHeader>
              <CardTitle>Recent Trades</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Signal Timestamp</TableHead>
                    <TableHead>Token</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Execution Price</TableHead>
                    <TableHead>PnL</TableHead>
                  </TableRow>
                </TableHeader>
                  <TableBody>
                    {portfolio.portfolioMetrics.map((metric: PortfolioMetric) => {
                      const tokenDetail = portfolio.portfolioDetails[metric.symbol]; // Fetch TokenDetail for the corresponding symbol

                      return (
                        <TableRow key={metric.symbol}>
                          {/* Adding TokenDetail Metrics */}
                          {tokenDetail && (
                            <>
                              <TableCell>{new Date(tokenDetail.signal_timestamp).toLocaleString()}</TableCell>
                            </>
                          )}
                          <TableCell>{metric.symbol}</TableCell>
                          <TableCell>{metric.token_amount >= 0 ? "Buy" : "Sell"}</TableCell>
                          <TableCell>${metric.signal_price.toFixed(3)}</TableCell>
                          <TableCell className={metric.PnL >= 0 ? "text-green-500" : "text-red-500"}>
                            ${metric.PnL.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
              </Table>
            </CardContent>
          </Card>


        </div>
      </CardContent>
    </Card>
  )
}
