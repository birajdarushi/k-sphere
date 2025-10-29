"use client"

import { useState, useEffect } from "react"
import useSWR from "swr"
import { AppSidebar } from "@/components/app-sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useToast } from "@/hooks/use-toast"
import { 
  FolderOpen, 
  Play, 
  Square, 
  Eye, 
  EyeOff, 
  Plus, 
  Trash2, 
  HardDrive, 
  FileCheck,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader2,
  RefreshCw
} from "lucide-react"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

interface IndexingStats {
  indexed_files: number
  failed_files: number
  skipped_files: number
  total_size: number
  current_path: string | null
  start_time: string | null
  end_time: string | null
}

export default function SystemIndexerPage() {
  const { toast } = useToast()
  const [newPath, setNewPath] = useState("")
  const [newExclusion, setNewExclusion] = useState("")
  const [showAddPathDialog, setShowAddPathDialog] = useState(false)
  const [showAddExclusionDialog, setShowAddExclusionDialog] = useState(false)
  const [maxFiles, setMaxFiles] = useState<string>("")

  // Fetch permitted paths
  const { data: pathsData, mutate: mutatePaths } = useSWR(
    "/api/system-indexer/permitted-paths",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch permitted paths")
      return response.json()
    }
  )

  // Fetch exclusion patterns
  const { data: exclusionsData, mutate: mutateExclusions } = useSWR(
    "/api/system-indexer/exclusions",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch exclusions")
      return response.json()
    }
  )

  // Fetch indexing status
  const { data: statusData, mutate: mutateStatus } = useSWR(
    "/api/system-indexer/status",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch status")
      return response.json()
    },
    { refreshInterval: 2000 } // Refresh every 2 seconds during indexing
  )

  // Fetch monitoring status
  const { data: monitoringData, mutate: mutateMonitoring } = useSWR(
    "/api/system-indexer/monitoring/status",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch monitoring status")
      return response.json()
    },
    { refreshInterval: 5000 }
  )

  // Fetch supported extensions
  const { data: extensionsData } = useSWR(
    "/api/system-indexer/supported-extensions",
    async (url) => {
      const response = await fetch(`${BACKEND_URL}${url}`)
      if (!response.ok) throw new Error("Failed to fetch extensions")
      return response.json()
    }
  )

  const handleAddPath = async () => {
    if (!newPath.trim()) return

    try {
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/permitted-paths`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: newPath.trim() })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Path Added",
          description: data.message
        })
        setNewPath("")
        setShowAddPathDialog(false)
        mutatePaths()
      } else {
        throw new Error(data.error || "Failed to add path")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to add path",
        variant: "destructive"
      })
    }
  }

  const handleRemovePath = async (path: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/permitted-paths`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Path Removed",
          description: data.message
        })
        mutatePaths()
      } else {
        throw new Error(data.error || "Failed to remove path")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to remove path",
        variant: "destructive"
      })
    }
  }

  const handleAddExclusion = async () => {
    if (!newExclusion.trim()) return

    try {
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/exclusions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pattern: newExclusion.trim() })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Exclusion Added",
          description: data.message
        })
        setNewExclusion("")
        setShowAddExclusionDialog(false)
        mutateExclusions()
      } else {
        throw new Error(data.error || "Failed to add exclusion")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to add exclusion",
        variant: "destructive"
      })
    }
  }

  const handleRemoveExclusion = async (pattern: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/exclusions`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pattern })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Exclusion Removed",
          description: data.message
        })
        mutateExclusions()
      } else {
        throw new Error(data.error || "Failed to remove exclusion")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to remove exclusion",
        variant: "destructive"
      })
    }
  }

  const handleStartIndexing = async () => {
    try {
      const payload = maxFiles ? { max_files: parseInt(maxFiles) } : {}
      
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Indexing Started",
          description: data.message
        })
        mutateStatus()
      } else {
        throw new Error(data.error || "Failed to start indexing")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to start indexing",
        variant: "destructive"
      })
    }
  }

  const handleStopIndexing = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/stop`, {
        method: "POST"
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Indexing Stopped",
          description: data.message
        })
        mutateStatus()
      } else {
        throw new Error(data.error || "Failed to stop indexing")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to stop indexing",
        variant: "destructive"
      })
    }
  }

  const handleCleanup = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/cleanup`, {
        method: "POST"
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Cleanup Complete",
          description: data.message || `Cleaned up ${data.cleaned} stuck files`
        })
        mutateStatus()
      } else {
        throw new Error(data.error || "Failed to cleanup files")
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to cleanup files",
        variant: "destructive"
      })
    }
  }

  const handleToggleMonitoring = async (enabled: boolean) => {
    try {
      const endpoint = enabled ? "start" : "stop"
      const response = await fetch(`${BACKEND_URL}/api/system-indexer/monitoring/${endpoint}`, {
        method: "POST"
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: enabled ? "Monitoring Started" : "Monitoring Stopped",
          description: data.message
        })
        mutateMonitoring()
      } else {
        throw new Error(data.error || `Failed to ${enabled ? "start" : "stop"} monitoring`)
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to toggle monitoring",
        variant: "destructive"
      })
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
  }

  const isIndexing = statusData?.in_progress || false
  const stats: IndexingStats = statusData?.stats || {}

  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      
      <main className="flex-1 p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">System-Wide Indexing</h1>
            <p className="text-muted-foreground mt-1">
              Index files across your entire system with permission
            </p>
          </div>
          
          {monitoringData?.watchdog_available === false && (
            <Alert className="w-auto">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                File monitoring disabled. Install watchdog library.
              </AlertDescription>
            </Alert>
          )}
        </div>

        {/* Indexing Status Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Indexing Status</CardTitle>
                <CardDescription>Current indexing progress and statistics</CardDescription>
              </div>
              
              <div className="flex items-center gap-2">
                {monitoringData?.watchdog_available && (
                  <div className="flex items-center gap-2 mr-4">
                    <Label htmlFor="auto-monitor">Auto-Monitor</Label>
                    <Switch
                      id="auto-monitor"
                      checked={monitoringData?.monitoring || false}
                      onCheckedChange={handleToggleMonitoring}
                    />
                  </div>
                )}
                
                {/* Cleanup Button */}
                <Button onClick={handleCleanup} variant="outline" size="sm">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Clean Up
                </Button>
                
                {isIndexing ? (
                  <Button onClick={handleStopIndexing} variant="destructive">
                    <Square className="mr-2 h-4 w-4" />
                    Stop Indexing
                  </Button>
                ) : (
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button>
                        <Play className="mr-2 h-4 w-4" />
                        Start Indexing
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Start System-Wide Indexing</DialogTitle>
                        <DialogDescription>
                          Index all files in permitted paths. This may take a while depending on the number of files.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="max-files">Max Files (Optional)</Label>
                          <Input
                            id="max-files"
                            type="number"
                            placeholder="Leave empty to index all files"
                            value={maxFiles}
                            onChange={(e) => setMaxFiles(e.target.value)}
                          />
                          <p className="text-sm text-muted-foreground">
                            Limit the number of files to index for testing
                          </p>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button onClick={handleStartIndexing}>
                          Start Indexing
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {isIndexing && stats.current_path && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Currently indexing: {stats.current_path}</span>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-muted-foreground">Indexed</span>
                </div>
                <p className="text-2xl font-bold">{stats.indexed_files || 0}</p>
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <span className="text-sm text-muted-foreground">Failed</span>
                </div>
                <p className="text-2xl font-bold">{stats.failed_files || 0}</p>
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm text-muted-foreground">Skipped</span>
                </div>
                <p className="text-2xl font-bold">{stats.skipped_files || 0}</p>
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-muted-foreground">Size</span>
                </div>
                <p className="text-2xl font-bold">{formatBytes(stats.total_size || 0)}</p>
              </div>
            </div>

            {stats.start_time && (
              <div className="text-sm text-muted-foreground">
                Started: {new Date(stats.start_time).toLocaleString()}
                {stats.end_time && ` • Ended: ${new Date(stats.end_time).toLocaleString()}`}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Configuration Tabs */}
        <Tabs defaultValue="paths" className="space-y-4">
          <TabsList>
            <TabsTrigger value="paths">Permitted Paths</TabsTrigger>
            <TabsTrigger value="exclusions">Exclusions</TabsTrigger>
            <TabsTrigger value="extensions">Supported Files</TabsTrigger>
          </TabsList>

          {/* Permitted Paths Tab */}
          <TabsContent value="paths" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Permitted Paths</CardTitle>
                    <CardDescription>
                      Add directories or files you want to index
                    </CardDescription>
                  </div>
                  
                  <Dialog open={showAddPathDialog} onOpenChange={setShowAddPathDialog}>
                    <DialogTrigger asChild>
                      <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Path
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add Permitted Path</DialogTitle>
                        <DialogDescription>
                          Enter the absolute path to a directory or file you want to index
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="new-path">Path</Label>
                          <Input
                            id="new-path"
                            placeholder="/Users/username/Documents"
                            value={newPath}
                            onChange={(e) => setNewPath(e.target.value)}
                          />
                          <p className="text-sm text-muted-foreground">
                            Examples: /Users/username/Documents, ~/Desktop, C:\Users\username\Documents
                          </p>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button onClick={handleAddPath}>Add Path</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                {pathsData?.paths?.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <FolderOpen className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No permitted paths configured</p>
                    <p className="text-sm">Add paths to start indexing your system</p>
                  </div>
                ) : (
                  <ScrollArea className="h-[300px]">
                    <div className="space-y-2">
                      {pathsData?.paths?.map((path: string) => (
                        <div
                          key={path}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div className="flex items-center gap-2">
                            <FolderOpen className="h-4 w-4 text-muted-foreground" />
                            <span className="font-mono text-sm">{path}</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemovePath(path)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Exclusions Tab */}
          <TabsContent value="exclusions" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Exclusion Patterns</CardTitle>
                    <CardDescription>
                      Patterns to exclude from indexing
                    </CardDescription>
                  </div>
                  
                  <Dialog open={showAddExclusionDialog} onOpenChange={setShowAddExclusionDialog}>
                    <DialogTrigger asChild>
                      <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Pattern
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add Exclusion Pattern</DialogTitle>
                        <DialogDescription>
                          Enter a path pattern to exclude from indexing
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="new-exclusion">Pattern</Label>
                          <Input
                            id="new-exclusion"
                            placeholder="node_modules/"
                            value={newExclusion}
                            onChange={(e) => setNewExclusion(e.target.value)}
                          />
                          <p className="text-sm text-muted-foreground">
                            Examples: node_modules/, .git/, temp/
                          </p>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button onClick={handleAddExclusion}>Add Pattern</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold mb-2">Default Exclusions</h4>
                  <ScrollArea className="h-[150px]">
                    <div className="flex flex-wrap gap-2">
                      {exclusionsData?.patterns?.default?.map((pattern: string) => (
                        <Badge key={pattern} variant="secondary">
                          {pattern}
                        </Badge>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
                
                <div>
                  <h4 className="text-sm font-semibold mb-2">Custom Exclusions</h4>
                  {exclusionsData?.patterns?.custom?.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No custom exclusions</p>
                  ) : (
                    <div className="space-y-2">
                      {exclusionsData?.patterns?.custom?.map((pattern: string) => (
                        <div
                          key={pattern}
                          className="flex items-center justify-between p-2 border rounded"
                        >
                          <span className="font-mono text-sm">{pattern}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveExclusion(pattern)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Supported Extensions Tab */}
          <TabsContent value="extensions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Supported File Types</CardTitle>
                <CardDescription>
                  File extensions that can be indexed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="flex flex-wrap gap-2">
                    {extensionsData?.extensions?.map((ext: string) => (
                      <Badge key={ext} variant="outline">
                        {ext}
                      </Badge>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
