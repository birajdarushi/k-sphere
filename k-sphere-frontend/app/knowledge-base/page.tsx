"use client"

import { AppSidebar } from "@/components/app-sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Upload, Search, FileText, ImageIcon, Mic, MoreVertical, Download, Trash2, Eye, Loader2, RefreshCw, ChevronDown, ChevronRight, Folder } from "lucide-react"
import { useState, useCallback, useRef } from "react"
import useSWR from "swr"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"

const mockFiles = [
  {
    id: 1,
    name: "machine_learning_fundamentals.pdf",
    type: "document",
    size: "2.4 MB",
    uploadedAt: "2024-01-15",
    status: "indexed",
    chunks: 45,
    preview:
      "This document covers the fundamental concepts of machine learning, including supervised and unsupervised learning, neural networks, and deep learning architectures...",
  },
  {
    id: 2,
    name: "neural_network_diagram.png",
    type: "image",
    size: "1.8 MB",
    uploadedAt: "2024-01-15",
    status: "indexed",
    chunks: 12,
    preview:
      "A detailed diagram showing the architecture of a neural network with input layer, hidden layers, and output layer.",
  },
  {
    id: 3,
    name: "conference_talk_2024.mp3",
    type: "audio",
    size: "15.2 MB",
    uploadedAt: "2024-01-14",
    status: "indexed",
    chunks: 89,
    preview:
      "Audio recording from the 2024 AI Conference discussing recent advances in transformer models and their applications...",
  },
  {
    id: 4,
    name: "research_paper_draft.pdf",
    type: "document",
    size: "3.1 MB",
    uploadedAt: "2024-01-14",
    status: "processing",
    chunks: 0,
    preview: "Draft research paper on novel approaches to reinforcement learning in robotics applications.",
  },
  {
    id: 5,
    name: "data_visualization.png",
    type: "image",
    size: "892 KB",
    uploadedAt: "2024-01-13",
    status: "indexed",
    chunks: 8,
    preview: "Chart showing performance metrics of different machine learning models on benchmark datasets.",
  },
  {
    id: 6,
    name: "interview_recording.mp3",
    type: "audio",
    size: "22.5 MB",
    uploadedAt: "2024-01-13",
    status: "indexed",
    chunks: 134,
    preview: "Interview with Dr. Smith discussing the future of artificial intelligence and ethical considerations.",
  },
  {
    id: 7,
    name: "technical_specification.pdf",
    type: "document",
    size: "4.7 MB",
    uploadedAt: "2024-01-12",
    status: "indexed",
    chunks: 67,
    preview:
      "Technical specifications for the new AI model deployment pipeline, including infrastructure requirements and scaling strategies.",
  },
  {
    id: 8,
    name: "architecture_blueprint.png",
    type: "image",
    size: "2.1 MB",
    uploadedAt: "2024-01-12",
    status: "indexed",
    chunks: 15,
    preview: "System architecture blueprint showing the microservices design for the AI platform.",
  },
]

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function KnowledgeBasePage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [filterType, setFilterType] = useState<string>("all")
  const [selectedFile, setSelectedFile] = useState<any>(null)
  const [uploadingFiles, setUploadingFiles] = useState<any[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { data, mutate } = useSWR("/api/knowledge-base", fetcher, {
    fallbackData: { files: mockFiles, total: mockFiles.length },
    refreshInterval: 5000,
    revalidateOnFocus: true,
  })
  const { toast } = useToast()

  const files = data?.files || []

  const handleFileUpload = useCallback(
    async (uploadedFiles: FileList | null) => {
      console.log("[v0] handleFileUpload called with:", uploadedFiles)
      if (!uploadedFiles || uploadedFiles.length === 0) {
        throw new Error("No files provided")
      }

      const tempFiles = Array.from(uploadedFiles).map((file, index) => ({
        id: `temp-${Date.now()}-${index}`,
        name: file.name,
        type: file.type.includes("pdf")
          ? "document"
          : file.type.includes("image")
            ? "image"
            : file.type.includes("audio")
              ? "audio"
              : "document",
        size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
        uploadedAt: new Date().toISOString().split("T")[0],
        status: "uploading",
        chunks: 0,
        preview: "Uploading file...",
      }))

      setUploadingFiles((prev) => [...prev, ...tempFiles])

      try {
        // Create a single FormData with all files
        const formData = new FormData()
        Array.from(uploadedFiles).forEach((file) => {
          formData.append("files", file) // Backend expects "files" (plural)
        })

        const response = await fetch("/api/knowledge-base", {
          method: "POST",
          body: formData,
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `Failed to upload files`)
        }

        await response.json()

        toast({
          title: "Upload successful",
          description: `${uploadedFiles.length} file(s) uploaded and processing started.`,
        })
        setUploadingFiles((prev) => prev.filter((f) => !tempFiles.find((tf) => tf.id === f.id)))
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
        mutate()
      } catch (error) {
        console.error("[v0] File upload error:", error)
        toast({
          title: "Upload failed",
          description:
            error instanceof Error ? error.message : "There was an error uploading your files. Please try again.",
          variant: "destructive",
        })
        setUploadingFiles((prev) => prev.filter((f) => !tempFiles.find((tf) => tf.id === f.id)))
      }
    },
    [mutate, toast],
  )

  const handleFileDelete = useCallback(
    async (fileId: string) => {
      try {
        const response = await fetch(`/api/knowledge-base/${fileId}`, {
          method: "DELETE",
        })

        if (response.ok) {
          toast({
            title: "File deleted",
            description: "The file has been removed from your knowledge base.",
          })
          mutate()
        } else {
          const errorData = await response.json()
          throw new Error(errorData.details || "Delete failed")
        }
      } catch (error) {
        console.error("[v0] File delete error:", error)
        toast({
          title: "Delete failed",
          description: error instanceof Error ? error.message : "There was an error deleting the file. Please try again.",
          variant: "destructive",
        })
      }
    },
    [mutate, toast],
  )

  const handleCleanupStuckFiles = useCallback(
    async () => {
      try {
        const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
        const response = await fetch(`${BACKEND_URL}/api/system-indexer/cleanup`, {
          method: "POST",
        })

        const data = await response.json()

        if (response.ok && data.success) {
          toast({
            title: "Cleanup Complete",
            description: data.message || `Deleted ${data.deleted} stuck files`,
          })
          mutate() // Refresh the file list
        } else {
          throw new Error(data.error || "Failed to cleanup files")
        }
      } catch (error) {
        console.error("[v0] Cleanup error:", error)
        toast({
          title: "Cleanup failed",
          description: error instanceof Error ? error.message : "There was an error cleaning up stuck files.",
          variant: "destructive",
        })
      }
    },
    [mutate, toast],
  )

  const allFiles = [...uploadingFiles, ...files]

  const filteredFiles = allFiles.filter((file: any) => {
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterType === "all" || file.type === filterType
    return matchesSearch && matchesFilter
  })

  // Group files by their directory path
  const groupedFiles = filteredFiles.reduce((acc: any, file: any) => {
    // Extract directory from path - get everything before the last /
    const pathParts = file.path?.split('/') || []
    let folderPath = 'Uploaded Files' // Default for manually uploaded files
    
    // If path has more than just filename, it's from system indexer
    if (pathParts.length > 1) {
      // Remove the filename (last part) and join back
      const dirParts = pathParts.slice(0, -1)
      folderPath = dirParts.join('/')
    }
    
    if (!acc[folderPath]) {
      acc[folderPath] = []
    }
    acc[folderPath].push(file)
    return acc
  }, {})

  const folderEntries = Object.entries(groupedFiles).sort((a: any, b: any) => {
    // Sort folders alphabetically
    return a[0].localeCompare(b[0])
  })

  const getFileIcon = (type: string) => {
    switch (type) {
      case "document":
        return <FileText className="h-5 w-5 text-primary" />
      case "image":
        return <ImageIcon className="h-5 w-5 text-chart-3" />
      case "audio":
        return <Mic className="h-5 w-5 text-chart-5" />
      default:
        return <FileText className="h-5 w-5 text-muted-foreground" />
    }
  }

  const getStatusBadge = (status: string) => {
    if (status === "indexed") {
      return (
        <Badge variant="outline" className="border-chart-2 bg-chart-2/10 text-chart-2">
          Indexed
        </Badge>
      )
    }
    if (status === "uploading") {
      return (
        <Badge variant="outline" className="border-primary bg-primary/10 text-primary">
          <Loader2 className="mr-1 h-3 w-3 animate-spin" />
          Uploading
        </Badge>
      )
    }
    return (
      <Badge variant="outline" className="border-chart-5 bg-chart-5/10 text-chart-5">
        <Loader2 className="mr-1 h-3 w-3 animate-spin" />
        Processing
      </Badge>
    )
  }

  return (
    <div className="flex h-screen">
      <AppSidebar />

      <main className="flex-1 overflow-y-auto bg-background">
        <div className="container mx-auto p-8">
          <div className="mb-8 flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Knowledge Base</h1>
              <p className="mt-2 text-muted-foreground">Manage and track your indexed files</p>
            </div>
            <Button
              onClick={handleCleanupStuckFiles}
              variant="outline"
              size="sm"
              className="border-destructive/50 text-destructive hover:bg-destructive hover:text-destructive-foreground"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Clean Up Stuck Files
            </Button>
          </div>

          {/* Upload Section */}
          <Card className={`mb-8 border-border bg-card p-8 transition-colors ${isDragOver ? 'border-primary bg-primary/5' : ''}`}
            onDrop={(e) => {
              e.preventDefault()
              setIsDragOver(false)
              const files = e.dataTransfer.files
              if (files.length > 0) {
                handleFileUpload(files)
              }
            }}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragOver(true)
            }}
            onDragLeave={(e) => {
              e.preventDefault()
              setIsDragOver(false)
            }}
          >
            <div className="flex flex-col items-center justify-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold text-foreground">Upload Files</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {isDragOver ? "Drop files here" : "Drag and drop files here, or click to browse"}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">Supports PDF, PNG, JPG, MP3, WAV</p>
              </div>
              <label htmlFor="file-upload">
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90" asChild>
                  <span>
                    <Upload className="mr-2 h-4 w-4" />
                    Select Files
                  </span>
                </Button>
              </label>
              <input
                ref={fileInputRef}
                id="file-upload"
                type="file"
                multiple
                accept=".pdf,.png,.jpg,.jpeg,.mp3,.wav"
                className="hidden"
                onChange={(e) => {
                  console.log("[v0] File input changed:", e.target.files)
                  handleFileUpload(e.target.files)
                }}
              />
            </div>
          </Card>

          {/* Search and Filter */}
          <div className="mb-6 flex flex-col gap-4 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-card border-border text-foreground"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={filterType === "all" ? "default" : "outline"}
                onClick={() => setFilterType("all")}
                className={filterType === "all" ? "bg-primary text-primary-foreground" : ""}
              >
                All
              </Button>
              <Button
                variant={filterType === "document" ? "default" : "outline"}
                onClick={() => setFilterType("document")}
                className={filterType === "document" ? "bg-primary text-primary-foreground" : ""}
              >
                <FileText className="mr-2 h-4 w-4" />
                Documents
              </Button>
              <Button
                variant={filterType === "image" ? "default" : "outline"}
                onClick={() => setFilterType("image")}
                className={filterType === "image" ? "bg-primary text-primary-foreground" : ""}
              >
                <ImageIcon className="mr-2 h-4 w-4" />
                Images
              </Button>
              <Button
                variant={filterType === "audio" ? "default" : "outline"}
                onClick={() => setFilterType("audio")}
                className={filterType === "audio" ? "bg-primary text-primary-foreground" : ""}
              >
                <Mic className="mr-2 h-4 w-4" />
                Audio
              </Button>
            </div>
          </div>

          {/* File List */}
          <Card className="border-border bg-card">
            <div className="divide-y divide-border">
              {folderEntries.map(([folderPath, folderFiles]: [string, any]) => {
                const isExpanded = expandedFolders.has(folderPath)
                const fileCount = folderFiles.length
                const displayPath = folderPath === 'Uploaded Files' ? folderPath : folderPath.replace(/^\/Users\/[^/]+/, '~')
                
                return (
                  <div key={folderPath}>
                    {/* Folder Header */}
                    <div
                      className="flex items-center gap-3 p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => {
                        const newExpanded = new Set(expandedFolders)
                        if (isExpanded) {
                          newExpanded.delete(folderPath)
                        } else {
                          newExpanded.add(folderPath)
                        }
                        setExpandedFolders(newExpanded)
                      }}
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                        <Folder className="h-5 w-5 text-muted-foreground" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{displayPath}</p>
                        <p className="text-xs text-muted-foreground">{fileCount} file{fileCount !== 1 ? 's' : ''}</p>
                      </div>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedFolder(folderPath)
                        }}
                        className="text-xs"
                      >
                        View All
                      </Button>

                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                    </div>

                    {/* Expanded Files */}
                    {isExpanded && (
                      <div className="bg-muted/30">
                        {folderFiles.map((file: any) => (
                          <div
                            key={file.id}
                            className="flex items-center gap-4 p-4 pl-16 hover:bg-muted/50 transition-colors cursor-pointer border-t border-border/50"
                            onClick={() => setSelectedFile(file)}
                          >
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-background">
                              {getFileIcon(file.type)}
                            </div>

                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
                              <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                                <span>{file.size}</span>
                                <span>•</span>
                                <span>{file.uploadedAt}</span>
                                <span>•</span>
                                <span>{file.chunks} chunks</span>
                              </div>
                            </div>

                            <div className="flex items-center gap-3">
                              {getStatusBadge(file.status)}

                              <DropdownMenu>
                                <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                                  <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="bg-popover border-border">
                                  <DropdownMenuItem
                                    className="text-popover-foreground hover:bg-accent"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${file.id}/view`
                                      window.open(url, "_blank")
                                    }}
                                  >
                                    <Eye className="mr-2 h-4 w-4" />
                                    Open
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    className="text-popover-foreground hover:bg-accent"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${file.id}/download`
                                      const a = document.createElement('a')
                                      a.href = url
                                      a.download = file.name
                                      a.click()
                                    }}
                                  >
                                    <Download className="mr-2 h-4 w-4" />
                                    Download
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    className="text-destructive hover:bg-destructive/10"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handleFileDelete(file.id)
                                    }}
                                  >
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </Card>

          {folderEntries.length === 0 && (
            <div className="mt-8 text-center">
              <p className="text-muted-foreground">No files found matching your search.</p>
            </div>
          )}
        </div>
      </main>

      <Dialog open={!!selectedFile} onOpenChange={() => setSelectedFile(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3">
              {selectedFile && getFileIcon(selectedFile.type)}
              {selectedFile?.name}
            </DialogTitle>
          </DialogHeader>

          {selectedFile && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant="outline">{selectedFile.type}</Badge>
                {getStatusBadge(selectedFile.status)}
                <Badge variant="outline">{selectedFile.size}</Badge>
              </div>

              {/* Audio Player for audio files */}
              {selectedFile.type === "audio" && (
                <div className="rounded-lg border border-border bg-muted p-4">
                  <h4 className="mb-3 text-sm font-semibold text-foreground">Audio Player</h4>
                  <audio 
                    controls 
                    className="w-full"
                    src={`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${selectedFile.id}/view`}
                  >
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}

              <div className="rounded-lg border border-border bg-muted p-6">
                <h4 className="mb-2 text-sm font-semibold text-foreground">Preview</h4>
                <p className="text-sm text-foreground">{selectedFile.preview}</p>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Uploaded:</span>
                  <span className="font-medium text-foreground">{selectedFile.uploadedAt}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Chunks:</span>
                  <span className="font-medium text-foreground">{selectedFile.chunks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span>{getStatusBadge(selectedFile.status)}</span>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button 
                  className="flex-1"
                  onClick={() => {
                    if (selectedFile) {
                      // Open file in new tab for viewing (not download)
                      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${selectedFile.id}/view`
                      window.open(url, "_blank")
                    }
                  }}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  Open Full Document
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    if (selectedFile) {
                      // Download file
                      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${selectedFile.id}/download`
                      const a = document.createElement("a")
                      a.href = url
                      a.download = selectedFile.name
                      document.body.appendChild(a)
                      a.click()
                      document.body.removeChild(a)
                    }
                  }}
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Folder View Modal */}
      <Dialog open={!!selectedFolder} onOpenChange={() => setSelectedFolder(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3">
              <Folder className="h-5 w-5" />
              {selectedFolder === 'Uploaded Files' ? selectedFolder : selectedFolder?.replace(/^\/Users\/[^/]+/, '~')}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-2">
            {selectedFolder && groupedFiles[selectedFolder]?.map((file: any) => (
              <div
                key={file.id}
                className="flex items-center gap-4 p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => {
                  setSelectedFolder(null)
                  setSelectedFile(file)
                }}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                  {getFileIcon(file.type)}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{file.size}</span>
                    <span>•</span>
                    <span>{file.chunks} chunks</span>
                    <span>•</span>
                    {getStatusBadge(file.status)}
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-popover border-border">
                    <DropdownMenuItem
                      className="text-popover-foreground hover:bg-accent"
                      onClick={(e) => {
                        e.stopPropagation()
                        const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${file.id}/view`
                        window.open(url, "_blank")
                      }}
                    >
                      <Eye className="mr-2 h-4 w-4" />
                      Open
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-popover-foreground hover:bg-accent"
                      onClick={(e) => {
                        e.stopPropagation()
                        const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/knowledge-base/${file.id}/download`
                        const a = document.createElement('a')
                        a.href = url
                        a.download = file.name
                        a.click()
                      }}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-destructive hover:bg-destructive/10"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleFileDelete(file.id)
                      }}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
