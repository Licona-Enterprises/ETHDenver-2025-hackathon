"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/use-toast"

import { MongoClient } from "mongodb"
import {MONGODB_URI} from "../../constants/consts"
import React, { useState } from "react";

import { useRouter } from "next/navigation"

interface AgentFormValues {
  agentName: string;
  strategyType: string;
  startingPortfolio: number;
  maxTradeFrequency: number;
  tokenPreference: string[];
  persona: string;
  knowledgeBase: File[]; // Now an array of files
  knowledgeBaseUrl: string[]; // Now an array of URLs
  TWITTER_API_KEY: string;
  TWITTER_API_KEY_SECRET: string;
  TWITTER_BEARER_TOKEN: string;
  TWITTER_ACCESS_TOKEN: string;
  TWITTER_ACCESS_TOKEN_SECRET: string;
  TWITTER_CLIENT_ID: string;
}

export default function LaunchAgentPage() {
  
  const router = useRouter()

  const [selectedTokens, setSelectedTokens] = useState<string[]>([])
  const [confirmationVisible, setConfirmationVisible] = useState(false); 

  const form = useForm<AgentFormValues>({
    defaultValues: {
      agentName: "",
      strategyType: "",
      startingPortfolio: 0,
      maxTradeFrequency: 1,
      tokenPreference: [],
      persona: "",
      knowledgeBase: [], // Now an array of files
      knowledgeBaseUrl: [], // Now an array of URLs
      TWITTER_API_KEY: "",
      TWITTER_API_KEY_SECRET: "",
      TWITTER_BEARER_TOKEN: "",
      TWITTER_ACCESS_TOKEN: "",
      TWITTER_ACCESS_TOKEN_SECRET: "",
      TWITTER_CLIENT_ID: "",
    },
  });

  const launchAgent = async (formData: AgentFormValues) => {
    try {
      const response = await fetch("/api/launch-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (data.success) {
        console.log("Agent launched successfully:", data.result);
        setConfirmationVisible(true);
        setTimeout(() => {
          router.push("/") // Redirect to home after a short delay
        }, 6000)
      } else {
        console.error("Failed to launch agent:", data.error);
      }
    } catch (error) {
      console.error("Error launching agent:", error);
    }
  };

  // const onSubmit = (values: AgentFormValues) => {
  //   const formattedData = {
  //     ...values,
  //     tokenPreference: selectedTokens,
  //     knowledgeBase: typeof values.knowledgeBase === "string" ? values.knowledgeBase : "",
  //     knowledgeBaseUrl: typeof values.knowledgeBaseUrl === "string" ? values.knowledgeBaseUrl : "",
  //   };
  //   launchAgent(formattedData);
  // };

  const onSubmit = (values: AgentFormValues) => {
    const formattedData = {
      ...values,
      tokenPreference: selectedTokens,
      knowledgeBase: values.knowledgeBase, // Get file names or handle uploads
      knowledgeBaseUrl: values.knowledgeBaseUrl, // Pass the array of URLs directly
    };
  
    launchAgent(formattedData);
  };
  

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Launch Agent</h1>

      {confirmationVisible ? (
        <ConfirmationScreen agentName={form.getValues("agentName")} />
      ) : (

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="agentName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Agent Name</FormLabel>
                <FormControl>
                  <Input placeholder="My Agent" {...field} />
                </FormControl>
                <FormDescription>Give your agent a unique name.</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />


          <FormField
            control={form.control}
            name="strategyType"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Strategy Type</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    placeholder="Enter strategy details"
                    {...field}
                  />
                </FormControl>
                <FormDescription>Enter the trading strategy for your agent.</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />



          {/* <FormField
            control={form.control}
            name="startingPortfolio"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Starting Portfolio</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    {...field}
                    onChange={(e) => field.onChange(+e.target.value)}
                  />
                </FormControl>
                <FormDescription>Enter the initial portfolio value in USD.</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          /> */}
          {/* <FormField
            control={form.control}
            name="maxTradeFrequency"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Maximum Trade Frequency (per hour)</FormLabel>
                <FormControl>
                  <Slider
                    min={1}
                    max={100}
                    step={1}
                    value={[field.value]}
                    onValueChange={(value) => field.onChange(value[0])}
                  />
                </FormControl>
                <FormDescription>Set the maximum number of trades per hour.</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          /> */}
          <FormField
            control={form.control}
            name="tokenPreference"
            render={() => (
              <FormItem>
                <FormLabel>Settlement Token Preference</FormLabel>
                <FormControl>
                  <div className="flex flex-wrap gap-2">
                    {["USDC", "DAI", "USDT", "WETH", "wstETH"].map((token) => (
                      <Button
                        key={token}
                        type="button"
                        variant={
                          selectedTokens.includes(token) ? "default" : "outline"
                        }
                        onClick={() => {
                          const newSelection = selectedTokens.includes(token)
                            ? selectedTokens.filter((t) => t !== token)
                            : [...selectedTokens, token];
                          setSelectedTokens(newSelection);
                          form.setValue("tokenPreference", newSelection);
                        }}
                      >
                        {token}
                      </Button>
                    ))}
                  </div>
                </FormControl>
                <FormDescription>Select the token your agent settle trades in.</FormDescription>
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
                <FormDescription>
                  Define your agent's persona and characteristics.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />


<FormField
  control={form.control}
  name="knowledgeBase"
  render={() => (
    <FormItem>
      <FormLabel>Knowledge Base</FormLabel>
      <FormControl>
        <div className="flex flex-col gap-4">
          {/* File Upload - Allows multiple files */}
          <Input
            type="file"
            accept=".txt,.pdf,.doc,.docx"
            multiple
            onChange={(e) => {
              const files = Array.from(e.target.files || []);
              form.setValue("knowledgeBase", files);
            }}
          />
          {/* Display selected files */}
          {form.watch("knowledgeBase")?.length > 0 && (
            <ul className="text-sm text-muted-foreground">
              {form.watch("knowledgeBase").map((file: File, index: number) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          )}

          <span className="text-sm text-muted-foreground">or</span>

          {/* URL Input - Allows multiple URLs */}
          <div className="flex flex-col gap-2">
            {form.watch("knowledgeBaseUrl").map((url, index) => (
              <div key={index} className="flex gap-2 items-center">
                <Input
                  type="url"
                  placeholder="Enter API Endpoint URL"
                  value={url}
                  onChange={(e) => {
                    const updatedUrls = [...form.watch("knowledgeBaseUrl")];
                    updatedUrls[index] = e.target.value;
                    form.setValue("knowledgeBaseUrl", updatedUrls);
                  }}
                />
                <button
                  type="button"
                  className="text-red-500 text-sm"
                  onClick={() => {
                    form.setValue(
                      "knowledgeBaseUrl",
                      form.watch("knowledgeBaseUrl").filter((_, i) => i !== index)
                    );
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
            <button
              type="button"
              className="text-blue-500 text-sm"
              onClick={() => form.setValue("knowledgeBaseUrl", [...form.watch("knowledgeBaseUrl"), ""])}
            >
              + Add URL
            </button>
          </div>
        </div>
      </FormControl>
      <FormDescription>
        Upload multiple files or provide multiple URLs for the agent's knowledge base.
      </FormDescription>
      <FormMessage />
    </FormItem>
  )}
/>



<FormField
            control={form.control}
            name="TWITTER_API_KEY"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Twitter API Key</FormLabel>
                <FormControl>
                  <Input placeholder="TTiDH..." {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

<FormField
            control={form.control}
            name="TWITTER_API_KEY_SECRET"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Twitter API Key Secret</FormLabel>
                <FormControl>
                  <Input placeholder="qPBBu..." {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

<FormField
            control={form.control}
            name="TWITTER_BEARER_TOKEN"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Twitter Bearer Token</FormLabel>
                <FormControl>
                  <Input placeholder="AAAAA..." {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="TWITTER_ACCESS_TOKEN"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Twitter Access Token</FormLabel>
                <FormControl>
                  <Input placeholder="15970..." {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="TWITTER_ACCESS_TOKEN_SECRET"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Twitter Access Token Secret</FormLabel>
                <FormControl>
                  <Input placeholder="udTmc..." {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="TWITTER_CLIENT_ID"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Twitter Client ID</FormLabel>
                <FormControl>
                  <Input placeholder="TFRLc..." {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit">Launch Agent</Button>
        </form>
      </Form>
      )}
    </div>
  );
}

// Confirmation Screen Component
const ConfirmationScreen: React.FC<{ agentName: string }> = ({ agentName }) => {
  return (
    <div className="flex flex-col items-center justify-center space-y-4 p-8 bg-black-100 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold">🎉 Success!</h2>
      <p>Your agent <span className="font-semibold">{agentName}</span> is being created.</p>
      <div className="animate-spin w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full"></div>
      <p className="text-gray-600">Please wait while we finalize the setup...</p>
    </div>
  );
};