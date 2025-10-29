"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { FileText, ImageIcon, Mic, Upload } from "lucide-react"
import { useState, useEffect } from "react"
import useSWR from "swr"

interface File {
  id: string
  name: string
  type: string
  size: string
  uploadedAt: string
  status: string
  chunks: number
}

interface FileSelectorDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  selectedFiles: string[]
  onFilesSelected: (fileIds: string[]) => void
}

export function FileSelectorDialog({
  open,
  onOpenChange,
  selectedFiles,
  onFilesSelected,
}: FileSelectorDialogProps) {
  const [localSelectedFiles, setLocalSelectedFiles] = useState<string[]>(selectedFiles)
  const { data: filesData } = useSWR(
    "/api/knowledge-base",
    async (url) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}${url}`)
      return response.json()
    },
    { revalidateOnFocus: false }
  )

  useEffect(() => {
    setLocalSelectedFiles(selectedFiles)
  }, [selectedFiles])

  const getFileIcon = (type: string) => {
    switch (type) {
      case "document":
        return <FileText className="h-4 w-4" />
      case "image":
        return <ImageIcon className="h-4 w-4" />
      case "audio":
        return <Mic className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const toggleFile = (fileId: string) => {
    setLocalSelectedFiles((prev) =>
      prev.includes(fileId) ? prev.filter((id) => id !== fileId) : [...prev, fileId]
    )
  }

  const handleApply = () => {
    onFilesSelected(localSelectedFiles)
    onOpenChange(false)
  }

  const handleClear = () => {
    setLocalSelectedFiles([])
  }

  const handleSelectAll = () => {
    if (filesData?.files) {
      setLocalSelectedFiles(filesData.files.map((f: File) => f.id))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Select Files for Chat Context</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Choose specific files to chat with. Only selected files will be used to answer your questions.
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleClear}>
                Clear
              </Button>
              <Button variant="outline" size="sm" onClick={handleSelectAll}>
                Select All
              </Button>
            </div>
          </div>

          {localSelectedFiles.length > 0 && (
            <Badge variant="secondary">
              {localSelectedFiles.length} file{localSelectedFiles.length !== 1 ? "s" : ""} selected
            </Badge>
          )}

          <div className="space-y-2">
            {filesData?.files?.map((file: File) => (
              <div
                key={file.id}
                className="flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-muted cursor-pointer"
                onClick={() => toggleFile(file.id)}
              >
                <Checkbox
                  checked={localSelectedFiles.includes(file.id)}
                  onCheckedChange={() => toggleFile(file.id)}
                />
                <div className="flex items-center gap-2 flex-1">
                  {getFileIcon(file.type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{file.size}</span>
                      <span>•</span>
                      <span>{file.chunks} chunks</span>
                      <span>•</span>
                      <span>{file.uploadedAt}</span>
                    </div>
                  </div>
                  <Badge variant="outline">{file.type}</Badge>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleApply}>
              Apply ({localSelectedFiles.length} selected)
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
