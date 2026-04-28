import { useState, useEffect } from 'react'
import { sessionsApi } from '../lib/api'
import { motion, AnimatePresence } from 'motion/react'
import { Calendar, Layers, RefreshCw, ChevronRight, UploadCloud, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface Session {
  _id: string
  event_name: string
  status: string
  created_at: string
  asset_count: number
  total_assets?: number
}

interface SessionsListProps {
  onUpload?: (sessionId: string) => void
}

export default function SessionsList({ onUpload }: SessionsListProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    setRefreshing(true)
    try {
      const data = await sessionsApi.getAll()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'completed': return { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' }
      case 'processing': return { color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' }
      case 'pending': return { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' }
      default: return { color: 'text-muted-foreground', bg: 'bg-white/5', border: 'border-white/10' }
    }
  }

  if (loading) {
    return (
      <div className="glass-card border-white/5 rounded-3xl p-12 flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-medium animate-pulse">Retrieving orchestration telemetry...</p>
      </div>
    )
  }

  return (
    <div className="glass-card border-white/5 rounded-3xl overflow-hidden">
      <div className="p-8 border-b border-white/5 bg-white/2 flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold tracking-tight">Deployment Sessions</h3>
          <p className="text-xs text-muted-foreground mt-1">Lifecycle management for orchestrated event pipelines</p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadSessions}
          disabled={refreshing}
          className="rounded-xl hover:bg-white/5 text-primary h-9 px-4"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>
      
      <div className="divide-y divide-white/5">
        <AnimatePresence mode="popLayout">
          {sessions.length === 0 ? (
            <div className="py-20 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto border border-white/5">
                <Layers className="w-8 h-8 text-muted-foreground/30" />
              </div>
              <p className="text-muted-foreground font-medium">No active orchestration sessions found.</p>
            </div>
          ) : (
            sessions.map((session, i) => {
              const status = getStatusConfig(session.status);
              return (
                <motion.div
                  key={session._id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="p-6 hover:bg-white/2 cursor-pointer transition-all group"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="font-bold text-lg tracking-tight group-hover:text-primary transition-colors">
                        {session.event_name}
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground font-medium">
                        <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded-lg border border-white/5">
                          <Layers className="w-3.5 h-3.5" />
                          {session.total_assets || session.asset_count || 0} Assets
                        </div>
                        <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded-lg border border-white/5">
                          <Calendar className="w-3.5 h-3.5" />
                          {new Date(session.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      {onUpload && (session.total_assets || session.asset_count || 0) < 50 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onUpload(session._id);
                          }}
                          className="hidden sm:flex rounded-xl border-primary/20 bg-primary/5 text-primary hover:bg-primary/10 hover:border-primary/30 h-9"
                        >
                          <UploadCloud className="w-4 h-4 mr-2" />
                          Resume Ingest
                        </Button>
                      )}
                      <Badge className={`${status.bg} ${status.color} ${status.border} border rounded-xl px-4 py-1.5 text-[10px] uppercase tracking-widest font-black min-w-[100px] flex justify-center`}>
                        {session.status}
                      </Badge>
                      <ChevronRight className="w-5 h-5 text-muted-foreground/30 group-hover:text-primary transition-colors group-hover:translate-x-1" />
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
