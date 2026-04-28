import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Upload, X, Check, AlertCircle, FileStack } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from './ui/badge'

interface BatchUploadProps {
  sessionId: string
  onUploadComplete: (assetCount: number) => void
}

export default function BatchUpload({ sessionId, onUploadComplete }: BatchUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const MIN_ASSETS = 50
  const MAX_ASSETS = 150

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif', 'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska']
    const validFiles = files.filter(file => allowedTypes.includes(file.type))

    if (validFiles.length !== files.length) {
      setError('Some files were excluded due to invalid type')
    } else {
      setError('')
    }
    setSelectedFiles(validFiles)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const files = Array.from(e.dataTransfer.files)
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif', 'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska']
    const validFiles = files.filter(file => allowedTypes.includes(file.type))

    if (validFiles.length !== files.length) {
      setError('Some files were excluded due to invalid type')
    } else {
      setError('')
    }
    setSelectedFiles(validFiles)
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select files to upload')
      return
    }
    if (selectedFiles.length < MIN_ASSETS) {
      setError(`Minimum ${MIN_ASSETS} assets required. You have ${selectedFiles.length}`)
      return
    }
    if (selectedFiles.length > MAX_ASSETS) {
      setError(`Maximum ${MAX_ASSETS} assets allowed. You have ${selectedFiles.length}`)
      return
    }

    setUploading(true)
    setError('')
    setProgress(0)

    try {
      const formData = new FormData()
      selectedFiles.forEach(file => {
        formData.append('files', file)
      })

      const response = await fetch(`http://localhost:8000/api/v1/upload/${sessionId}/files`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const data = await response.json()
      setProgress(100)

      setTimeout(() => {
        onUploadComplete(data.total_assets)
        setSelectedFiles([])
        setUploading(false)
      }, 500)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploading(false)
    }
  }

  return (
    <div className="glass-card border-white/5 rounded-3xl p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold tracking-tight">Upload Assets</h3>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
          <FileStack className="w-3 h-3" />
          {MIN_ASSETS}-{MAX_ASSETS} required
        </div>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 group ${uploading
            ? 'border-white/5 bg-white/2 cursor-not-allowed'
            : 'border-white/10 hover:border-primary/50 hover:bg-white/2 cursor-pointer'
          }`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,video/*"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />

        <AnimatePresence mode="wait">
          {selectedFiles.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto group-hover:scale-110 transition-transform duration-300">
                <Upload className="w-8 h-8 text-primary/60" />
              </div>
              <div>
                <p className="text-lg font-semibold">Drop assets here</p>
                <p className="text-sm text-muted-foreground max-w-xs mx-auto mt-2">
                  Drag & drop images or videos, or click to browse files from your computer.
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="selected"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mx-auto shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                <Check className="w-8 h-8 text-emerald-400" />
              </div>
              <div>
                <p className="text-lg font-bold">{selectedFiles.length} Assets Selected</p>
                <div className="flex items-center justify-center gap-2 mt-2">
                  {selectedFiles.length < MIN_ASSETS && (
                    <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">
                      Add {MIN_ASSETS - selectedFiles.length} more
                    </Badge>
                  )}
                  {selectedFiles.length >= MIN_ASSETS && selectedFiles.length <= MAX_ASSETS && (
                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
                      Validation Passed
                    </Badge>
                  )}
                  {selectedFiles.length > MAX_ASSETS && (
                    <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">
                      Remove {selectedFiles.length - MAX_ASSETS} files
                    </Badge>
                  )}
                </div>
              </div>
              <div className="flex gap-3 justify-center pt-2" onClick={(e) => e.stopPropagation()}>
                <Button
                  variant="ghost"
                  onClick={() => setSelectedFiles([])}
                  className="h-10 px-6 rounded-xl hover:bg-white/5"
                  disabled={uploading}
                >
                  <X className="mr-2 h-4 w-4" />
                  Clear All
                </Button>
                <Button
                  onClick={handleUpload}
                  disabled={uploading || selectedFiles.length < MIN_ASSETS || selectedFiles.length > MAX_ASSETS}
                  className="h-10 px-8 rounded-xl shadow-lg shadow-primary/20"
                >
                  {uploading ? 'Processing Stream...' : 'Start Ingest'}
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {uploading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-3"
          >
            <div className="flex justify-between text-xs font-bold uppercase tracking-wider text-muted-foreground">
              <span>Streaming Data</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-2 bg-white/5 shadow-inner" />
            <p className="text-xs text-center text-muted-foreground italic">
              Encapsulating {selectedFiles.length} assets into the processing pipeline...
            </p>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400 rounded-2xl">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="p-4 rounded-2xl bg-white/2 border border-white/5">
        <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold flex items-center gap-2">
          <AlertCircle className="w-3 h-3" />
          Ingest Rules: JPEG, PNG, WebP, HEIC | MP4, MOV, AVI | 50-150 units
        </p>
      </div>
    </div>
  )
}
