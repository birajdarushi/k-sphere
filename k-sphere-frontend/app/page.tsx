"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  Activity,
  Database,
  FileText,
  ImageIcon,
  Mic,
  TrendingUp,
  Clock,
  CheckCircle2,
  Search,
  Sparkles,
  ExternalLink,
  FileIcon,
  XCircle,
  AlertCircle,
} from "lucide-react"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((res) => res.json())

const mockSearchResults = [
  {
    id: 1,
    title: "Introduction to Machine Learning",
    snippet:
      "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data. It enables computers to improve their performance on tasks through experience...",
    source: "machine_learning_fundamentals.pdf",
    type: "document",
    relevance: 0.95,
    page: 3,
  },
  {
    id: 2,
    title: "Neural Network Architecture Diagram",
    snippet:
      "Visual representation of a deep neural network with multiple hidden layers, showing the flow of information from input to output...",
    source: "neural_network_diagram.png",
    type: "image",
    relevance: 0.89,
  },
  {
    id: 3,
    title: "Deep Learning Conference Talk 2024",
    snippet:
      "In this presentation, we discuss the latest advances in deep learning architectures, including transformer models and their applications in natural language processing...",
    source: "conference_talk_2024.mp3",
    type: "audio",
    relevance: 0.87,
    timestamp: "12:34",
  },
  {
    id: 4,
    title: "Python Programming Best Practices",
    snippet: "Learn essential Python coding standards and best practices for writing clean, maintainable code...",
    source: "python_guide.pdf",
    type: "document",
    relevance: 0.82,
    page: 15,
  },
  {
    id: 5,
    title: "Data Visualization Techniques",
    snippet: "Comprehensive guide to creating effective data visualizations using modern tools and libraries...",
    source: "data_viz_tutorial.pdf",
    type: "document",
    relevance: 0.78,
    page: 7,
  },
]

// Helper function to clean filename by removing UUID prefix
const cleanFileName = (fileName: string): string => {
  // Remove UUID prefix pattern (e.g., "832afd58-3df7-4fce-9305-99ada90c01e5_")
  return fileName.replace(/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}_/, '')
}

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [suggestions, setSuggestions] = useState<typeof mockSearchResults>([])
  const [searchResults, setSearchResults] = useState<typeof mockSearchResults>([])
  const [isSearching, setIsSearching] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<(typeof mockSearchResults)[0] | null>(null)

  const { data: systemStatus, error: systemError } = useSWR("/api/system-status", fetcher, {
    refreshInterval: 5000, // Refresh every 5 seconds
  })

  const { data: kbStats, error: kbError } = useSWR("/api/knowledge-base/stats", fetcher, {
    refreshInterval: 3000, // Refresh every 3 seconds for real-time updates
  })

  const { data: recentActivity } = useSWR("/api/knowledge-base?limit=5&sort=recent", fetcher, {
    refreshInterval: 2000, // Refresh every 2 seconds for activity feed
  })

  const getSystemStatus = () => {
    if (systemError || !systemStatus) {
      return { status: "offline", text: "System Offline", icon: XCircle, color: "text-destructive" }
    }

    // Backend returns: { status: "online"/"offline"/"partial", services: {...} }
    if (systemStatus.status === "online") {
      return { status: "online", text: "All Services Running", icon: CheckCircle2, color: "text-chart-2" }
    }

    if (systemStatus.status === "partial") {
      return { status: "partial", text: "Partial Services", icon: AlertCircle, color: "text-chart-5" }
    }

    return { status: "offline", text: "Services Offline", icon: XCircle, color: "text-destructive" }
  }

  const systemStatusInfo = getSystemStatus()

  useEffect(() => {
    if (searchQuery.trim().length > 2) {
      const timer = setTimeout(async () => {
        try {
          const response = await fetch("/api/chat/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: searchQuery, limit: 3 }),
          })
          
          if (response.ok) {
            const data = await response.json()
            // Transform backend results to match frontend format
            const allResults = data.results?.map((result: any, index: number) => {
              const cleanName = cleanFileName(result.fileName || "Unknown")
              return {
                id: index + 1,
                title: cleanName,
                snippet: result.snippet || "",
                source: cleanName,
                type: result.type || "document",
                relevance: result.relevanceScore || 0,
              }
            }) || []
            
            // Group by filename and keep only the best match for each file
            const groupedByFile = allResults.reduce((acc: any, result: any) => {
              const fileName = result.title
              if (!acc[fileName] || result.relevance > acc[fileName].relevance) {
                acc[fileName] = result
              }
              return acc
            }, {})
            
            // Convert back to array and sort by relevance
            const transformedResults = Object.values(groupedByFile)
              .sort((a: any, b: any) => b.relevance - a.relevance)
              .slice(0, 5) as any[] // Limit to top 5 results
            
            setSuggestions(transformedResults)
            setShowSuggestions(transformedResults.length > 0)
          }
        } catch (error) {
          console.error("Search suggestions error:", error)
          setShowSuggestions(false)
        }
      }, 300)

      return () => clearTimeout(timer)
    } else {
      setShowSuggestions(false)
      setSuggestions([])
    }
  }, [searchQuery])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setIsSearching(true)
    setShowSuggestions(false)

    try {
      const response = await fetch("/api/chat/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, limit: 10 }),
      })

      if (response.ok) {
        const data = await response.json()
        // Transform backend results to match frontend format
        const transformedResults = data.results?.map((result: any, index: number) => {
          const cleanName = cleanFileName(result.fileName || "Unknown")
          return {
            id: index + 1,
            title: cleanName,
            snippet: result.snippet || "",
            source: cleanName,
            type: result.type || "document",
            relevance: result.relevanceScore || 0,
            metadata: result.metadata,
          }
        }) || []
        
        setSearchResults(transformedResults)
      } else {
        console.error("Search failed:", response.statusText)
        setSearchResults([])
      }
    } catch (error) {
      console.error("Search error:", error)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleSuggestionClick = (suggestion: (typeof mockSearchResults)[0]) => {
    setSearchQuery(suggestion.title)
    setShowSuggestions(false)
    setSearchResults([suggestion])
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case "document":
        return <FileText className="h-5 w-5 text-primary" />
      case "image":
        return <ImageIcon className="h-5 w-5 text-chart-3" />
      case "audio":
        return <Mic className="h-5 w-5 text-chart-5" />
      default:
        return <FileIcon className="h-5 w-5 text-muted-foreground" />
    }
  }

  return (
    <div className="flex h-screen">
      <AppSidebar />

      <main className="flex-1 overflow-y-auto bg-background">
        <div className="container mx-auto p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">K-Sphere</h1>
            <p className="text-muted-foreground mb-6">Search your entire knowledge base</p>

            <form onSubmit={handleSearch} className="relative">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search documents, images, audio files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => searchQuery.length > 2 && setShowSuggestions(true)}
                  className="h-14 pl-12 pr-32 text-base shadow-lg"
                />
                <Button
                  type="submit"
                  size="sm"
                  className="absolute right-2 top-1/2 -translate-y-1/2"
                  disabled={isSearching}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  {isSearching ? "Searching..." : "Search"}
                </Button>
              </div>

              {showSuggestions && suggestions.length > 0 && (
                <Card className="absolute z-50 mt-2 w-full border-border bg-card shadow-xl">
                  <div className="p-2">
                    <p className="px-3 py-2 text-xs font-medium text-muted-foreground">Suggestions</p>
                    {suggestions.map((suggestion) => (
                      <button
                        key={suggestion.id}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="flex w-full items-start gap-3 rounded-lg p-3 text-left transition-colors hover:bg-muted"
                      >
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                          {getFileIcon(suggestion.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-foreground truncate">{suggestion.title}</p>
                          <p className="text-xs text-muted-foreground truncate">{suggestion.snippet}</p>
                          <div className="mt-1 flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {Math.round(suggestion.relevance)}% match
                            </Badge>
                            <span className="text-xs text-muted-foreground">{suggestion.source}</span>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </Card>
              )}
            </form>
          </div>

          {searchResults.length > 0 && (
            <div className="mb-8">
              <h2 className="mb-4 text-xl font-semibold text-foreground">Search Results ({searchResults.length})</h2>
              <div className="space-y-4">
                {searchResults.map((result) => (
                  <Card
                    key={result.id}
                    className="cursor-pointer border-border bg-card p-6 transition-all hover:border-primary/50 hover:shadow-md"
                    onClick={() => setSelectedDoc(result)}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-muted">
                        {getFileIcon(result.type)}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="mb-2 flex items-center gap-2">
                          <h3 className="text-lg font-semibold text-primary hover:underline">{result.title}</h3>
                          <Badge variant="outline" className="text-xs">
                            {Math.round(result.relevance)}% match
                          </Badge>
                        </div>

                        <p className="mb-3 text-sm text-foreground">{result.snippet}</p>

                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <FileIcon className="h-3 w-3" />
                            {result.source}
                          </span>
                          {result.page && <span>Page {result.page}</span>}
                          {result.timestamp && <span>Timestamp: {result.timestamp}</span>}
                        </div>
                      </div>

                      <Button variant="ghost" size="icon" className="shrink-0">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* System Status - only show when no search results */}
          {searchResults.length === 0 && (
            <>
              <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-border bg-card p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Files</p>
                      <p className="mt-2 text-3xl font-bold text-foreground">
                        {kbStats?.totalFiles?.toLocaleString() || "0"}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {kbStats?.totalChunks?.toLocaleString() || "0"} chunks
                      </p>
                    </div>
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <Database className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                </Card>

                <Card className="border-border bg-card p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Documents</p>
                      <p className="mt-2 text-3xl font-bold text-foreground">
                        {kbStats?.byType?.documents?.toLocaleString() || "0"}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">PDFs, DOCX, TXT</p>
                    </div>
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                </Card>

                <Card className="border-border bg-card p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Images</p>
                      <p className="mt-2 text-3xl font-bold text-foreground">
                        {kbStats?.byType?.images?.toLocaleString() || "0"}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">With OCR</p>
                    </div>
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-chart-3/10">
                      <ImageIcon className="h-6 w-6 text-chart-3" />
                    </div>
                  </div>
                </Card>

                <Card className="border-border bg-card p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Audio Files</p>
                      <p className="mt-2 text-3xl font-bold text-foreground">
                        {kbStats?.byType?.audio?.toLocaleString() || "0"}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">Transcribed</p>
                    </div>
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-chart-5/10">
                      <Mic className="h-6 w-6 text-chart-5" />
                    </div>
                  </div>
                </Card>
              </div>

              {/* AI Models Status */}
              <div className="mb-8">
                <h2 className="mb-4 text-xl font-semibold text-foreground">AI Models Status</h2>
                <div className="grid gap-4 md:grid-cols-3">
                  <Card className="border-border bg-card p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Embedding Model</p>
                        <p className="mt-1 text-lg font-semibold text-foreground">
                          {systemStatus?.services?.embeddings?.model || "nomic-embed-text"}
                        </p>
                      </div>
                      {systemStatus?.services?.embeddings?.status === "available" ? (
                        <CheckCircle2 className="h-5 w-5 text-chart-2" />
                      ) : (
                        <XCircle className="h-5 w-5 text-destructive" />
                      )}
                    </div>
                    <div className="mt-4 flex items-center gap-2">
                      <Activity
                        className={`h-4 w-4 ${systemStatus?.services?.embeddings?.status === "available" ? "text-chart-2" : "text-destructive"}`}
                      />
                      <span className="text-xs text-muted-foreground">
                        {systemStatus?.services?.embeddings?.status === "available" ? "Operational" : "Offline"}
                      </span>
                    </div>
                  </Card>

                  <Card className="border-border bg-card p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">LLM</p>
                        <p className="mt-1 text-lg font-semibold text-foreground">
                          {systemStatus?.services?.ollama?.model || "llama3.2:3b"}
                        </p>
                      </div>
                      {systemStatus?.services?.ollama?.status === "running" ? (
                        <CheckCircle2 className="h-5 w-5 text-chart-2" />
                      ) : (
                        <XCircle className="h-5 w-5 text-destructive" />
                      )}
                    </div>
                    <div className="mt-4 flex items-center gap-2">
                      <Activity
                        className={`h-4 w-4 ${systemStatus?.services?.ollama?.status === "running" ? "text-chart-2" : "text-destructive"}`}
                      />
                      <span className="text-xs text-muted-foreground">
                        {systemStatus?.services?.ollama?.status === "running" ? "Operational" : "Offline"}
                      </span>
                    </div>
                  </Card>

                  <Card className="border-border bg-card p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Vector Database</p>
                        <p className="mt-1 text-lg font-semibold text-foreground">
                          ChromaDB
                        </p>
                      </div>
                      {systemStatus?.services?.vectorDb?.status === "connected" ? (
                        <CheckCircle2 className="h-5 w-5 text-chart-2" />
                      ) : (
                        <XCircle className="h-5 w-5 text-destructive" />
                      )}
                    </div>
                    <div className="mt-4 flex items-center gap-2">
                      <Activity
                        className={`h-4 w-4 ${systemStatus?.services?.vectorDb?.status === "connected" ? "text-chart-2" : "text-destructive"}`}
                      />
                      <span className="text-xs text-muted-foreground">
                        {systemStatus?.services?.vectorDb?.collections || 0} collections
                      </span>
                    </div>
                  </Card>
                </div>
              </div>

              {/* Recent Activity */}
              <div>
                <h2 className="mb-4 text-xl font-semibold text-foreground">Recent Activity</h2>
                <Card className="border-border bg-card">
                  <div className="divide-y divide-border">
                    {recentActivity?.files && recentActivity.files.length > 0 ? (
                      recentActivity.files.map((file: any, index: number) => {
                        const getActivityIcon = (type: string) => {
                          switch (type) {
                            case "document":
                              return FileText
                            case "image":
                              return ImageIcon
                            case "audio":
                              return Mic
                            default:
                              return FileIcon
                          }
                        }
                        const Icon = getActivityIcon(file.type)

                        // Format time difference
                        const getTimeAgo = (uploadedAt: string) => {
                          const now = new Date()
                          const uploaded = new Date(uploadedAt)
                          const diffMs = now.getTime() - uploaded.getTime()
                          const diffMins = Math.floor(diffMs / 60000)
                          
                          if (diffMins < 1) return "Just now"
                          if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`
                          const diffHours = Math.floor(diffMins / 60)
                          if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`
                          const diffDays = Math.floor(diffHours / 24)
                          return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`
                        }

                        const getActionText = (status: string, type: string) => {
                          if (status === "indexed") {
                            if (type === "document") return "Document indexed"
                            if (type === "image") return "Image processed"
                            if (type === "audio") return "Audio transcribed"
                          }
                          return "File uploaded"
                        }

                        return (
                          <div key={file.id || index} className="flex items-center gap-4 p-4">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                              <Icon className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-medium text-foreground">
                                {getActionText(file.status, file.type)}
                              </p>
                              <p className="text-xs text-muted-foreground">{file.name}</p>
                              {file.chunks > 0 && (
                                <p className="text-xs text-muted-foreground">{file.chunks} chunks indexed</p>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              {getTimeAgo(file.uploadedAt)}
                            </div>
                          </div>
                        )
                      })
                    ) : (
                      <div className="p-8 text-center">
                        <Activity className="mx-auto h-12 w-12 text-muted-foreground opacity-50" />
                        <p className="mt-4 text-sm text-muted-foreground">No recent activity</p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          Upload files to see them here
                        </p>
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            </>
          )}
        </div>
      </main>

      <Dialog open={!!selectedDoc} onOpenChange={() => setSelectedDoc(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3">
              {selectedDoc && getFileIcon(selectedDoc.type)}
              {selectedDoc?.title}
            </DialogTitle>
          </DialogHeader>

          {selectedDoc && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant="outline">{selectedDoc.type}</Badge>
                <Badge variant="outline">{Math.round(selectedDoc.relevance * 100)}% relevance</Badge>
              </div>

              <div className="rounded-lg border border-border bg-muted p-6">
                <p className="text-sm text-foreground">{selectedDoc.snippet}</p>
              </div>

              <div className="space-y-2 text-sm text-muted-foreground">
                <p>
                  <strong>Source:</strong> {selectedDoc.source}
                </p>
                {selectedDoc.page && (
                  <p>
                    <strong>Page:</strong> {selectedDoc.page}
                  </p>
                )}
                {selectedDoc.timestamp && (
                  <p>
                    <strong>Timestamp:</strong> {selectedDoc.timestamp}
                  </p>
                )}
              </div>

              <div className="flex gap-3">
                <Button 
                  className="flex-1"
                  onClick={() => {
                    const fileId = (selectedDoc as any)?.metadata?.file_id
                    if (fileId) {
                      // Open file using file_id from metadata
                      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${fileId}/download`
                      window.open(url, "_blank")
                    }
                  }}
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Open Full Document
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    const fileId = (selectedDoc as any)?.metadata?.file_id
                    if (fileId && selectedDoc?.source) {
                      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${fileId}/download`
                      const a = document.createElement("a")
                      a.href = url
                      a.download = selectedDoc.source
                      document.body.appendChild(a)
                      a.click()
                      document.body.removeChild(a)
                    }
                  }}
                >
                  Download
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
