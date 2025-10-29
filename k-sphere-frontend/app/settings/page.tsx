"use client"

import { useState, useEffect } from "react"
import useSWR from "swr"
import { AppSidebar } from "@/components/app-sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"
import { Database, Cpu, HardDrive, SettingsIcon, Download, RefreshCw } from "lucide-react"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export default function SettingsPage() {
  const { toast } = useToast()
  const [watchDirectory, setWatchDirectory] = useState("/data/input")
  const [chunkSize, setChunkSize] = useState("512")
  const [chunkOverlap, setChunkOverlap] = useState("50")
  const [topKResults, setTopKResults] = useState("5")
  
  // Model selection states
  const [selectedLLM, setSelectedLLM] = useState("")
  const [selectedEmbedding, setSelectedEmbedding] = useState("")
  const [newModelName, setNewModelName] = useState("")
  const [isPulling, setIsPulling] = useState(false)
  const [pullingModel, setPullingModel] = useState("")
  const [showPullDialog, setShowPullDialog] = useState(false)

  // Fetch available models
  const { data: modelsData, mutate: mutateModels, isLoading: modelsLoading } = useSWR(
    "/api/settings/models",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch models")
      return response.json()
    },
    { refreshInterval: 5000 } // Refresh every 5 seconds to check for new models
  )

  // Fetch current settings
  const { data: settingsData, mutate: mutateSettings } = useSWR(
    "/api/settings",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch settings")
      return response.json()
    }
  )

  // Initialize selected models from current settings
  useEffect(() => {
    if (modelsData?.current) {
      setSelectedLLM(modelsData.current.llm || "")
      setSelectedEmbedding(modelsData.current.embedding || "")
    }
  }, [modelsData])

  // Initialize other settings
  useEffect(() => {
    if (settingsData?.settings) {
      const s = settingsData.settings
      setChunkSize(s.chunk_size?.toString() || "512")
      setChunkOverlap(s.chunk_overlap?.toString() || "50")
      setTopKResults(s.top_k?.toString() || "5")
      setWatchDirectory(s.watch_directory || "/data/input")
    }
  }, [settingsData])

  const handleSwitchModel = async (type: "llm" | "embedding", modelName: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/settings/models/switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_type: type, model_name: modelName })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Model Switched",
          description: `Now using ${modelName} for ${type === "llm" ? "chat" : "embeddings"}`
        })
        mutateModels()
        mutateSettings()
      } else {
        throw new Error(data.detail || "Failed to switch model")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to switch model",
        variant: "destructive"
      })
    }
  }

  const handlePullModel = async () => {
    if (!newModelName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a model name",
        variant: "destructive"
      })
      return
    }

    setIsPulling(true)
    setPullingModel(newModelName)

    try {
      const response = await fetch(`${BACKEND_URL}/api/settings/models/pull`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_name: newModelName })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Pulling Model",
          description: data.message || `Started pulling ${newModelName}. This may take a few minutes.`
        })
        setShowPullDialog(false)
        setNewModelName("")
        
        // Poll for model availability
        const pollInterval = setInterval(async () => {
          try {
            const statusResponse = await fetch(
              `${BACKEND_URL}/api/settings/models/pull-status/${newModelName}`
            )
            const statusData = await statusResponse.json()
            
            if (statusData.available) {
              clearInterval(pollInterval)
              setIsPulling(false)
              setPullingModel("")
              toast({
                title: "Model Ready",
                description: `${newModelName} is now available`
              })
              mutateModels()
            }
          } catch (error) {
            console.error("Error checking pull status:", error)
          }
        }, 3000) // Check every 3 seconds

        // Stop polling after 10 minutes
        setTimeout(() => {
          clearInterval(pollInterval)
          setIsPulling(false)
          setPullingModel("")
        }, 600000)
      } else {
        throw new Error(data.detail || "Failed to pull model")
      }
    } catch (error: any) {
      setIsPulling(false)
      setPullingModel("")
      toast({
        title: "Error",
        description: error.message || "Failed to pull model",
        variant: "destructive"
      })
    }
  }

  const handleSaveSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          settings: {
            chunk_size: parseInt(chunkSize),
            chunk_overlap: parseInt(chunkOverlap),
            top_k: parseInt(topKResults),
            watch_directory: watchDirectory
          }
        })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Settings Saved",
          description: "Your settings have been updated"
        })
        mutateSettings()
      } else {
        throw new Error(data.detail || "Failed to save settings")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to save settings",
        variant: "destructive"
      })
    }
  }

  return (
    <div className="flex h-screen">
      <AppSidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Settings</h1>
            <p className="mt-2 text-muted-foreground">Configure your K-Sphere system</p>
          </div>

          {/* Model Configuration */}
          <div className="mb-8">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-foreground">Model Configuration</h2>
              <Dialog open={showPullDialog} onOpenChange={setShowPullDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Download className="mr-2 h-4 w-4" />
                    Pull New Model
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Pull Ollama Model</DialogTitle>
                    <DialogDescription>
                      Enter the name of the model you want to download from Ollama.
                      Examples: llama3.2, mistral, codellama, gemma:7b
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-4">
                    <Label htmlFor="model-name">Model Name</Label>
                    <Input
                      id="model-name"
                      placeholder="e.g., mistral, gemma:7b, llama3.2"
                      value={newModelName}
                      onChange={(e) => setNewModelName(e.target.value)}
                      className="mt-2"
                      disabled={isPulling}
                    />
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowPullDialog(false)} disabled={isPulling}>
                      Cancel
                    </Button>
                    <Button onClick={handlePullModel} disabled={isPulling}>
                      {isPulling ? (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Pulling...
                        </>
                      ) : (
                        "Pull Model"
                      )}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            
            {isPulling && pullingModel && (
              <div className="mb-4 rounded-lg border border-blue-500/50 bg-blue-500/10 p-4">
                <div className="flex items-center gap-3">
                  <RefreshCw className="h-5 w-5 animate-spin text-blue-500" />
                  <div>
                    <p className="font-semibold text-blue-500">Pulling {pullingModel}</p>
                    <p className="text-sm text-muted-foreground">This may take several minutes depending on model size...</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="grid gap-4 md:grid-cols-2">
              <Card className="border-border bg-card p-6">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-1/10">
                    <Cpu className="h-5 w-5 text-chart-1" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">LLM Model</h3>
                    <Badge variant="outline" className="mt-1 border-chart-2 bg-chart-2/10 text-chart-2">
                      Active
                    </Badge>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm text-muted-foreground">Select Model</Label>
                    {modelsLoading ? (
                      <div className="mt-1 flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Loading models...</span>
                      </div>
                    ) : (
                      <Select 
                        value={selectedLLM} 
                        onValueChange={(val) => {
                          setSelectedLLM(val)
                          handleSwitchModel("llm", val)
                        }}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select LLM model" />
                        </SelectTrigger>
                        <SelectContent>
                          {modelsData?.available?.length > 0 ? (
                            modelsData.available.map((model: string) => (
                              <SelectItem key={model} value={model}>
                                {model}
                              </SelectItem>
                            ))
                          ) : (
                            <SelectItem value="none" disabled>
                              No models available
                            </SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                  <div>
                    <Label className="text-sm text-muted-foreground">Current Model</Label>
                    <Input 
                      value={modelsData?.current?.llm || "Loading..."} 
                      readOnly 
                      className="mt-1 border-border bg-muted text-foreground font-mono text-sm" 
                    />
                  </div>
                </div>
              </Card>

              <Card className="border-border bg-card p-6">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-2/10">
                    <Database className="h-5 w-5 text-chart-2" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Embedding Model</h3>
                    <Badge variant="outline" className="mt-1 border-chart-2 bg-chart-2/10 text-chart-2">
                      Active
                    </Badge>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm text-muted-foreground">Select Model</Label>
                    {modelsLoading ? (
                      <div className="mt-1 flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Loading models...</span>
                      </div>
                    ) : (
                      <Select 
                        value={selectedEmbedding} 
                        onValueChange={(val) => {
                          setSelectedEmbedding(val)
                          handleSwitchModel("embedding", val)
                        }}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select embedding model" />
                        </SelectTrigger>
                        <SelectContent>
                          {modelsData?.available?.length > 0 ? (
                            modelsData.available.map((model: string) => (
                              <SelectItem key={model} value={model}>
                                {model}
                              </SelectItem>
                            ))
                          ) : (
                            <SelectItem value="none" disabled>
                              No models available
                            </SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                  <div>
                    <Label className="text-sm text-muted-foreground">Current Model</Label>
                    <Input 
                      value={modelsData?.current?.embedding || "Loading..."} 
                      readOnly 
                      className="mt-1 border-border bg-muted text-foreground font-mono text-sm" 
                    />
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Storage Configuration */}
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-semibold text-foreground">Storage Configuration</h2>
            <Card className="border-border bg-card p-6">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-4/10">
                  <HardDrive className="h-5 w-5 text-chart-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Vector Database</h3>
                  <Badge variant="outline" className="mt-1 border-chart-2 bg-chart-2/10 text-chart-2">
                    Connected
                  </Badge>
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-sm text-muted-foreground">Database Type</Label>
                  <Input value="ChromaDB" readOnly className="mt-1 border-border bg-muted text-foreground" />
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Storage Path</Label>
                  <Input value="/data/chroma" readOnly className="mt-1 border-border bg-muted text-foreground" />
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Collection Name</Label>
                  <Input value="k-sphere-knowledge" readOnly className="mt-1 border-border bg-muted text-foreground" />
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Total Vectors</Label>
                  <Input value="15,847" readOnly className="mt-1 border-border bg-muted text-foreground" />
                </div>
              </div>
            </Card>
          </div>

          {/* System Settings */}
          <div>
            <h2 className="mb-4 text-lg font-semibold text-foreground">System Settings</h2>
            <Card className="border-border bg-card p-6">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <SettingsIcon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground">General Settings</h3>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-sm text-muted-foreground">Watch Directory</Label>
                  <Input
                    value={watchDirectory}
                    onChange={(e) => setWatchDirectory(e.target.value)}
                    className="mt-1 border-border bg-background text-foreground"
                  />
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Chunk Size</Label>
                  <Input
                    value={chunkSize}
                    onChange={(e) => setChunkSize(e.target.value)}
                    className="mt-1 border-border bg-background text-foreground"
                  />
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Chunk Overlap</Label>
                  <Input
                    value={chunkOverlap}
                    onChange={(e) => setChunkOverlap(e.target.value)}
                    className="mt-1 border-border bg-background text-foreground"
                  />
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Top K Results</Label>
                  <Input
                    value={topKResults}
                    onChange={(e) => setTopKResults(e.target.value)}
                    className="mt-1 border-border bg-background text-foreground"
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end">
                <Button onClick={handleSaveSettings} className="bg-primary text-primary-foreground hover:bg-primary/90">
                  Save Changes
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
