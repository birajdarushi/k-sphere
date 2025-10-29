"use client"

import { useState, useEffect } from "react"
import { MessageSquare, Plus, Trash2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ApiClient } from "@/lib/api-client"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface Conversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messageCount: number
}

interface ConversationSidebarProps {
  currentConversationId: string
  onConversationSelect: (conversationId: string) => void
  onNewChat: () => void
  isVisible: boolean
  onToggle: () => void
}

export function ConversationSidebar({ 
  currentConversationId, 
  onConversationSelect,
  onNewChat,
  isVisible,
  onToggle
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null)

  const loadConversations = async () => {
    try {
      const response = await ApiClient.getConversations()
      setConversations(response.conversations || [])
    } catch (error) {
      console.error("Failed to load conversations:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent triggering conversation select
    setConversationToDelete(conversationId)
  }

  const confirmDelete = async () => {
    if (!conversationToDelete) return

    try {
      await ApiClient.deleteConversation(conversationToDelete)
      setConversations(prev => prev.filter(c => c.id !== conversationToDelete))
      
      // If deleted conversation was active, trigger new chat
      if (conversationToDelete === currentConversationId) {
        onNewChat()
      }
      
      setConversationToDelete(null)
    } catch (error) {
      console.error("Failed to delete conversation:", error)
      // Could add a toast notification here instead of alert
      setConversationToDelete(null)
    }
  }

  useEffect(() => {
    loadConversations()
    
    // Refresh conversations every 30 seconds
    const interval = setInterval(loadConversations, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMs = now.getTime() - date.getTime()
    const diffInHours = diffInMs / (1000 * 60 * 60)
    const diffInDays = diffInMs / (1000 * 60 * 60 * 24)

    if (diffInHours < 1) {
      return "Just now"
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`
    } else if (diffInDays < 7) {
      return `${Math.floor(diffInDays)}d ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  if (!isVisible) return null

  return (
    <div className="flex h-full w-80 flex-col border-r border-border bg-card">
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b border-border px-4 flex-shrink-0">
        <h2 className="text-lg font-semibold text-foreground">Chat History</h2>
        <div className="flex items-center gap-2">
          <Button
            onClick={onNewChat}
            size="sm"
            className="h-8 w-8 p-0"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 space-y-1">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-sm text-muted-foreground">Loading...</div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 px-4">
              <MessageSquare className="h-12 w-12 text-muted-foreground/50 mb-2" />
              <p className="text-sm text-muted-foreground text-center">
                No conversations yet. Start a new chat!
              </p>
            </div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={cn(
                  "w-full rounded-lg transition-colors hover:bg-muted group relative",
                  currentConversationId === conversation.id && "bg-muted"
                )}
              >
                <button
                  onClick={() => onConversationSelect(conversation.id)}
                  className="w-full text-left p-3 pr-12"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <h3 className="text-sm font-medium text-foreground truncate">
                          {conversation.title}
                        </h3>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{conversation.messageCount} messages</span>
                        <span>•</span>
                        <span>{formatDate(conversation.updatedAt)}</span>
                      </div>
                    </div>
                  </div>
                </button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => handleDeleteConversation(conversation.id, e)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive hover:text-destructive-foreground"
                  title="Delete conversation"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={conversationToDelete !== null} onOpenChange={(open) => !open && setConversationToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Delete?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete this conversation and all its messages.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setConversationToDelete(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
