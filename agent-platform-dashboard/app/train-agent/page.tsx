"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  agentToTrain: z.string(),
  trainingDataset: z.string(),
  trainingGoals: z.array(z.string()).min(1, {
    message: "Select at least one training goal.",
  }),
  persona: z.string().min(10, {
    message: "Persona must be at least 10 characters.",
  }),
  knowledgeBase: z
    .instanceof(File)
    .optional()
    .or(
      z.string().min(1, {
        message: "Please upload a knowledge base file or enter a URL.",
      }),
    ),
})

const agents = [
  { id: "1", name: "Agent Alpha" },
  { id: "2", name: "Agent Beta" },
  { id: "3", name: "Agent Gamma" },
]

const datasets = [
  { id: "1", name: "Last 30 days" },
  { id: "2", name: "Last 90 days" },
  { id: "3", name: "Last 365 days" },
]

const trainingGoals = [
  { id: "roi", label: "Maximize ROI" },
  { id: "losses", label: "Minimize Losses" },
  { id: "sharpe", label: "Improve Sharpe Ratio" },
]

export default function TrainAgentPage() {
  const [isTraining, setIsTraining] = useState(false)
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState<string[]>([])
  const [trainingResults, setTrainingResults] = useState<string>("")

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agentToTrain: "",
      trainingDataset: "",
      trainingGoals: [],
      persona: "",
      knowledgeBase: undefined,
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
    setIsTraining(true)
    setProgress(0)
    setLogs([])
    setTrainingResults("")

    // Simulating training process
    const interval = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= 100) {
          clearInterval(interval)
          setIsTraining(false)
          setLogs((prevLogs) => [...prevLogs, "Training completed successfully!"])
          setTrainingResults(
            "Training Results:\n\n" +
              "Initial Performance:\n" +
              "ROI: 5.2%\n" +
              "Sharpe Ratio: 0.8\n" +
              "Max Drawdown: 12%\n\n" +
              "Final Performance:\n" +
              "ROI: 7.8%\n" +
              "Sharpe Ratio: 1.2\n" +
              "Max Drawdown: 8%\n\n" +
              "Improvement:\n" +
              "ROI: +2.6%\n" +
              "Sharpe Ratio: +0.4\n" +
              "Max Drawdown: -4%",
          )
          return 100
        }
        const newProgress = prevProgress + 10
        setLogs((prevLogs) => [...prevLogs, `Training progress: ${newProgress}%`])
        return newProgress
      })
    }, 1000)
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Train Agent</h1>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="agentToTrain"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Agent to Train</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select an agent" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {agents.map((agent) => (
                      <SelectItem key={agent.id} value={agent.id}>
                        {agent.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="trainingDataset"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Define Training Dataset</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a dataset" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {datasets.map((dataset) => (
                      <SelectItem key={dataset.id} value={dataset.id}>
                        {dataset.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="trainingGoals"
            render={() => (
              <FormItem>
                <FormLabel>Set Training Goals</FormLabel>
                <div className="space-y-2">
                  {trainingGoals.map((goal) => (
                    <FormField
                      key={goal.id}
                      control={form.control}
                      name="trainingGoals"
                      render={({ field }) => (
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value?.includes(goal.id)}
                              onCheckedChange={(checked) => {
                                const updatedGoals = checked
                                  ? [...field.value, goal.id]
                                  : field.value?.filter((value) => value !== goal.id)
                                field.onChange(updatedGoals)
                              }}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{goal.label}</FormLabel>
                        </FormItem>
                      )}
                    />
                  ))}
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="persona"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Agent Persona</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Describe your agent's personality and behavior..."
                    className="resize-none"
                    {...field}
                  />
                </FormControl>
                <FormDescription>Define or update your agent's persona and characteristics.</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="knowledgeBase"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Knowledge Base</FormLabel>
                <FormControl>
                  <div className="flex items-center gap-4">
                    <Input
                      type="file"
                      accept=".txt,.pdf,.doc,.docx"
                      onChange={(e) => field.onChange(e.target.files?.[0])}
                    />
                    <span className="text-sm text-muted-foreground">or</span>
                    <Input
                      type="url"
                      placeholder="Enter knowledge base URL"
                      onChange={(e) => field.onChange(e.target.value)}
                    />
                  </div>
                </FormControl>
                <FormDescription>Upload a file or provide a URL to update the agent's knowledge base.</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" disabled={isTraining}>
            {isTraining ? "Training..." : "Start Training"}
          </Button>
        </form>
      </Form>

      {isTraining && (
        <Card>
          <CardHeader>
            <CardTitle>Training Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={progress} className="w-full" />
            <div className="mt-4 h-40 overflow-auto bg-muted p-2 rounded-md">
              {logs.map((log, index) => (
                <p key={index}>{log}</p>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {trainingResults && (
        <Card>
          <CardHeader>
            <CardTitle>Training Results</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap bg-muted p-2 rounded-md">{trainingResults}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

