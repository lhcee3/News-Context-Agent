"use client"

import type React from "react"
import { useState } from "react"
import { Search, Send, Sparkles, Clock, TrendingUp } from "lucide-react"
import { CustomButton } from "@/components/ui/custom-button"
import { CustomInput } from "@/components/ui/custom-input"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/custom-card"

export default function NewsContextTool() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<{ text: string; type: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        let errorDetails
        try {
          errorDetails = await response.json()
        } catch {
          errorDetails = await response.text()
        }

        console.error("API Error:", errorDetails)
        throw new Error(`Failed to fetch data from the API: ${JSON.stringify(errorDetails)}`)
      }

      const data = await response.json()

      if (data?.response) {
        setResults([{ text: data.response, type: "response" }])
      } else {
        setError("No response from the API.")
      }
    } catch (err: any) {
      console.error("Error fetching data:", err)
      setResults([])
      setError(err.message || "Error fetching data from the backend.")
    }

    setLoading(false)
  }

  const getIconForType = (type: string) => {
    switch (type) {
      case "trend":
        return <TrendingUp className="text-emerald-400" size={20} />
      case "history":
        return <Clock className="text-amber-400" size={20} />
      default:
        return <Sparkles className="text-blue-400" size={20} />
    }
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <header className="mb-12 mt-10 text-center">
        <div className="inline-block mb-4 relative">
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 mb-1 pb-2">
            News Context & Evolution Agent
          </h1>
          <div className="absolute -inset-1 blur-xl bg-blue-600/20 -z-10 rounded-full"></div>
        </div>
        <p className="text-gray-400 max-w-xl mx-auto">
          Ask questions to understand news context, trends, and historical evolution
        </p>
      </header>

      <Card className="p-6 mb-8 overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 to-transparent pointer-events-none"></div>
        <form onSubmit={handleSubmit} className="flex gap-3 relative z-10">
          <div className="relative flex-1 group">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 group-focus-within:text-blue-400 transition-colors"
              size={18}
            />
            <div className="absolute -inset-0.5 bg-blue-600/20 rounded-md blur-md opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
            <CustomInput
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about news context..."
              className="pl-10 relative"
            />
          </div>
          <CustomButton type="submit" disabled={loading || !query.trim()} className="min-w-[50px] group">
            {loading ? (
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
            ) : (
              <Send size={18} className="group-hover:translate-x-0.5 transition-transform" />
            )}
          </CustomButton>
        </form>
      </Card>

      {error && (
        <div className="text-center py-16 px-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {results.length > 0 && (
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Context Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-5 bg-gradient-to-r from-gray-900 to-gray-800 rounded-md border border-gray-800 shadow-sm">
              {results.map((result, index) => (
                <div
                  key={index}
                  className="flex gap-3 mb-4 last:mb-0 pb-4 last:pb-0 border-b last:border-b-0 border-gray-800"
                >
                  <div className="mt-0.5 shrink-0">{getIconForType(result.type)}</div>
                  <p className="text-gray-200">{result.text}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
