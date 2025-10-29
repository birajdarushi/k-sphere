"use client"

import { AppSidebar } from "@/components/app-sidebar"
import { ConversationSidebar } from "@/components/conversation-sidebar"
import { FileSelectorDialog } from "@/components/file-selector-dialog"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Send, ImageIcon, Mic, FileText, ExternalLink, Square, Plus, PanelLeftClose, PanelLeft, Filter } from "lucide-react"
import { useState, useEffect, useRef } from "react"
import { cn } from "@/lib/utils"
import { ApiClient } from "@/lib/api-client"

interface Message {
  id: number
  role: "user" | "assistant"
  content: string
  sources?: Array<{
    name: string
    type: string
    relevance: number
    timestamp?: string
    startTime?: number
    endTime?: number
  }>
  timestamp: string
}

const mockMessages: Message[] = [
  {
    id: 1,
    role: "user",
    content: "What are the key principles of machine learning?",
    timestamp: "10:30 AM",
  },
  {
    id: 2,
    role: "assistant",
    content:
      "Based on your knowledge base, the key principles of machine learning include:\n\n1. **Supervised Learning**: Training models on labeled data to make predictions\n2. **Unsupervised Learning**: Finding patterns in unlabeled data\n3. **Feature Engineering**: Selecting and transforming relevant input variables\n4. **Model Evaluation**: Using metrics like accuracy, precision, and recall\n5. **Generalization**: Ensuring models perform well on unseen data\n\nThese principles form the foundation for building effective ML systems.",
    sources: [
      { name: "machine_learning_fundamentals.pdf", type: "document", relevance: 0.95 },
      { name: "research_paper_draft.pdf", type: "document", relevance: 0.82 },
      { name: "technical_specification.pdf", type: "document", relevance: 0.76 },
    ],
    timestamp: "10:30 AM",
  },
  {
    id: 3,
    role: "user",
    content: "Can you explain the neural network architecture shown in my diagrams?",
    timestamp: "10:32 AM",
  },
  {
    id: 4,
    role: "assistant",
    content:
      "The neural network architecture in your diagrams shows a deep learning model with the following structure:\n\n**Input Layer**: Receives raw data (784 neurons for 28x28 images)\n**Hidden Layers**: Three fully connected layers with 512, 256, and 128 neurons respectively, using ReLU activation\n**Output Layer**: 10 neurons with softmax activation for classification\n\nThe architecture uses dropout layers (0.2 rate) between hidden layers to prevent overfitting. This is a classic feedforward neural network design suitable for image classification tasks.",
    sources: [
      { name: "neural_network_diagram.png", type: "image", relevance: 0.98 },
      { name: "architecture_blueprint.png", type: "image", relevance: 0.88 },
    ],
    timestamp: "10:32 AM",
  },
]

export default function ChatPage() {
  const [mounted, setMounted] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [typingMessageId, setTypingMessageId] = useState<number | null>(null)
  const [conversationId, setConversationId] = useState<string>(`chat-${Date.now()}`)
  const [chatTitle, setChatTitle] = useState<string>("New Chat")
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [titleGenerated, setTitleGenerated] = useState<boolean>(false)
  const [isSidebarVisible, setIsSidebarVisible] = useState<boolean>(true)
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]) // File IDs for filtering
  const [showFileSelector, setShowFileSelector] = useState<boolean>(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleNewChat = () => {
    setMessages([])
    const newId = `chat-${Date.now()}`
    setConversationId(newId)
    setChatTitle("New Chat")
    setTitleGenerated(false)
  }

  const handleConversationSelect = async (selectedConversationId: string) => {
    try {
      setIsLoading(true)
      const response = await ApiClient.getConversationHistory(selectedConversationId)
      
      // Transform backend messages to frontend format
      const loadedMessages: Message[] = response.messages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        sources: msg.sources || [],
        timestamp: new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }))
      
      setMessages(loadedMessages)
      setConversationId(selectedConversationId)
      setTitleGenerated(true) // Mark title as already generated for this conversation
      
      // Update chat title from first message
      if (loadedMessages.length > 0) {
        const firstUserMessage = loadedMessages.find(m => m.role === "user")
        if (firstUserMessage) {
          const title = firstUserMessage.content.length > 50 
            ? firstUserMessage.content.substring(0, 47) + "..."
            : firstUserMessage.content
          setChatTitle(title)
        }
      }
    } catch (error) {
      console.error("Failed to load conversation:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStopGeneration = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
      setIsLoading(false)
      setTypingMessageId(null)
    }
  }

  const generateChatTitle = async (firstMessage: string) => {
    try {
      // Simple title generation - take first 50 chars or first sentence
      const title = firstMessage.length > 50 
        ? firstMessage.substring(0, 47) + "..."
        : firstMessage
      setChatTitle(title)
      
      // Update the title in the backend
      await ApiClient.updateConversationTitle(conversationId, title)
    } catch (error) {
      console.error("Failed to generate chat title:", error)
    }
  }

  const handleVoiceRecording = async () => {
    if (isRecording) {
      // Stop recording
      if (mediaRecorder) {
        mediaRecorder.stop()
        setIsRecording(false)
      }
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const recorder = new MediaRecorder(stream)
        const audioChunks: Blob[] = []

        recorder.ondataavailable = (event) => {
          audioChunks.push(event.data)
        }

        recorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
          
          // Send to backend for transcription
          try {
            setIsLoading(true)
            const formData = new FormData()
            formData.append('file', audioBlob)

            const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/chat/transcribe`, {
              method: 'POST',
              body: formData,
            })

            if (response.ok) {
              const data = await response.json()
              setInputValue(data.transcription)
            }
          } catch (error) {
            console.error('Failed to transcribe audio:', error)
          } finally {
            setIsLoading(false)
          }

          // Stop all tracks
          stream.getTracks().forEach(track => track.stop())
        }

        recorder.start()
        setMediaRecorder(recorder)
        setIsRecording(true)
      } catch (error) {
        console.error('Failed to access microphone:', error)
        alert('Could not access microphone. Please check permissions.')
      }
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    // Generate chat title from first message ONLY once
    if (messages.length === 0 && !titleGenerated) {
      generateChatTitle(inputValue)
      setTitleGenerated(true)
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    // Create abort controller for cancellation
    const controller = new AbortController()
    setAbortController(controller)

    try {
      const assistantMessageId = Date.now() + 1
      
      // Create initial assistant message with empty content
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }

      setMessages((prev) => [...prev, assistantMessage])
      setTypingMessageId(assistantMessageId)

      // Use streaming endpoint
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: userMessage.content,
          conversationId: conversationId,
          fileIds: selectedFiles.length > 0 ? selectedFiles : undefined
        }),
        signal: controller.signal
      })

      if (!response.ok) {
        throw new Error(`Failed to get response: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error("No response body")
      }

      let buffer = ""
      let sources: any[] = []

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6))
            
            if (data.type === "sources") {
              sources = data.sources.map((source: any) => ({
                name: source.fileName || "Unknown",
                type: source.metadata?.type || "document",
                relevance: source.relevanceScore || 0,
                timestamp: source.metadata?.timestamp || null,
                startTime: source.metadata?.start_time || null,
                endTime: source.metadata?.end_time || null,
              }))
              // Update message with sources
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, sources }
                    : msg
                )
              )
            } else if (data.type === "token") {
              // Append token to message content
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: msg.content + data.token }
                    : msg
                )
              )
            } else if (data.type === "done") {
              setTypingMessageId(null)
            } else if (data.type === "error") {
              console.error("Streaming error:", data.error)
              throw new Error(data.error)
            }
          }
        }
      }

    } catch (error: any) {
      // Don't show error if user cancelled
      if (error.name === 'AbortError') {
        console.log("Generation cancelled by user")
        return
      }
      
      console.error("Chat error:", error)
      const errorMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please make sure you have uploaded files to the knowledge base and try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }
      setMessages((prev) => [...prev, errorMessage])
      setTypingMessageId(null)
    } finally {
      setIsLoading(false)
      setAbortController(null)
    }
  }

  const getSourceIcon = (type: string) => {
    switch (type) {
      case "document":
        return <FileText className="h-3 w-3" />
      case "image":
        return <ImageIcon className="h-3 w-3" />
      case "audio":
        return <Mic className="h-3 w-3" />
      default:
        return <FileText className="h-3 w-3" />
    }
  }

  return (
    <div className="flex h-screen">
      <AppSidebar />
      <ConversationSidebar 
        currentConversationId={conversationId}
        onConversationSelect={handleConversationSelect}
        onNewChat={handleNewChat}
        isVisible={isSidebarVisible}
        onToggle={() => setIsSidebarVisible(!isSidebarVisible)}
      />

      <main className="flex flex-1 flex-col">
        <div className="border-b border-border bg-card px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarVisible(!isSidebarVisible)}
              className="h-8 w-8"
              title={isSidebarVisible ? "Hide chat history" : "Show chat history"}
            >
              {isSidebarVisible ? <PanelLeftClose className="h-5 w-5" /> : <PanelLeft className="h-5 w-5" />}
            </Button>
            <div>
              <h1 className="text-xl font-semibold text-foreground">{chatTitle}</h1>
              <p className="text-sm text-muted-foreground">Ask questions about your knowledge base</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFileSelector(true)}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              {selectedFiles.length > 0 ? `${selectedFiles.length} files selected` : "Select Files"}
            </Button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="mx-auto max-w-4xl space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn("flex gap-4", message.role === "user" ? "justify-end" : "justify-start")}
              >
                {message.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary">
                    <span className="font-mono text-xs font-bold text-primary-foreground">K</span>
                  </div>
                )}

                <div className={cn("flex max-w-[80%] flex-col gap-2", message.role === "user" && "items-end")}>
                  <Card
                    className={cn(
                      "border-border p-4",
                      message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card",
                    )}
                  >
                    <p
                      className={cn(
                        "whitespace-pre-wrap text-sm leading-relaxed",
                        message.role === "user" ? "text-primary-foreground" : "text-foreground",
                      )}
                    >
                      {message.content}
                      {typingMessageId === message.id && (
                        <span className="inline-block w-[2px] h-4 ml-1 bg-current animate-pulse" />
                      )}
                    </p>
                  </Card>

                  {message.sources && message.sources.length > 0 && (
                    <div className="flex flex-col gap-2">
                      <p className="text-xs font-medium text-muted-foreground">Sources:</p>
                      <div className="flex flex-wrap gap-2">
                        {(() => {
                          // Group sources by filename
                          const groupedSources = message.sources.reduce((acc: any, source) => {
                            if (!source || !source.name) return acc
                            
                            const cleanName = source.name.split('/').pop()?.replace(/^[a-f0-9-]+_/, '') || source.name
                            if (!acc[cleanName]) {
                              acc[cleanName] = {
                                name: cleanName,
                                fullName: source.name,
                                type: source.type,
                                count: 0,
                                maxRelevance: 0,
                                relevances: [],
                                timestamps: []
                              }
                            }
                            acc[cleanName].count++
                            acc[cleanName].relevances.push(source.relevance)
                            acc[cleanName].maxRelevance = Math.max(acc[cleanName].maxRelevance, source.relevance)
                            if (source.timestamp) {
                              acc[cleanName].timestamps.push({
                                timestamp: source.timestamp,
                                startTime: source.startTime,
                                endTime: source.endTime
                              })
                            }
                            return acc
                          }, {})

                          return Object.values(groupedSources).map((group: any, index) => (
                            <Badge
                              key={index}
                              variant="outline"
                              className="cursor-pointer border-border bg-card text-foreground hover:bg-muted"
                              onClick={() => {
                                // For audio files with timestamps, open with time parameter
                                if (group.type === 'audio' && group.timestamps.length > 0) {
                                  const firstTimestamp = group.timestamps[0]
                                  window.open(`http://localhost:8000/uploads/${group.fullName}#t=${Math.floor(firstTimestamp.startTime)}`, '_blank')
                                } else {
                                  window.open(`http://localhost:8000/uploads/${group.fullName}`, '_blank')
                                }
                              }}
                            >
                              <div className="flex items-center gap-2">
                                {getSourceIcon(group.type)}
                                <span className="text-xs truncate max-w-[200px]" title={group.fullName}>
                                  {group.name}
                                </span>
                                {group.timestamps.length > 0 && (
                                  <span className="text-xs font-mono text-primary">
                                    {group.timestamps[0].timestamp}
                                  </span>
                                )}
                                {group.count > 1 && (
                                  <span className="text-xs font-semibold text-primary">
                                    ({group.count} sections)
                                  </span>
                                )}
                                <span className="text-xs text-muted-foreground">
                                  {Math.round(group.maxRelevance)}%
                                </span>
                                <ExternalLink className="h-3 w-3" />
                              </div>
                            </Badge>
                          ))
                        })()}
                      </div>
                    </div>
                  )}

                  <span className="text-xs text-muted-foreground">{message.timestamp}</span>
                </div>

                {message.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                    <span className="text-xs font-medium text-foreground">You</span>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-border bg-card p-6">
          <div className="mx-auto max-w-4xl">
            <div className="flex items-end gap-3">
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="icon" 
                  className={cn(
                    "h-10 w-10 border-border hover:bg-muted bg-transparent",
                    isRecording && "bg-red-500 text-white hover:bg-red-600"
                  )}
                  onClick={handleVoiceRecording}
                  title={isRecording ? "Stop Recording" : "Start Voice Recording"}
                >
                  <Mic className="h-5 w-5" />
                </Button>
              </div>

              <div className="flex-1">
                <Input
                  placeholder="Ask a question about your knowledge base..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  className="min-h-[40px] resize-none border-border bg-background text-foreground"
                />
              </div>

              <Button
                onClick={isLoading ? handleStopGeneration : handleSend}
                disabled={!isLoading && !inputValue.trim()}
                className={cn(
                  "h-10",
                  isLoading 
                    ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" 
                    : "bg-primary text-primary-foreground hover:bg-primary/90"
                )}
              >
                {isLoading ? (
                  <Square className="h-5 w-5 fill-current" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>

            <p className="mt-3 text-center text-xs text-muted-foreground">
              K-Sphere uses your local knowledge base to answer questions. All processing happens offline.
            </p>
          </div>
        </div>
      </main>

      <FileSelectorDialog
        open={showFileSelector}
        onOpenChange={setShowFileSelector}
        selectedFiles={selectedFiles}
        onFilesSelected={setSelectedFiles}
      />
    </div>
  )
}
