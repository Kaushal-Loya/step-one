import { useState } from 'react'
import { motion } from 'motion/react'
import { FileCheck, Activity, AlertCircle, Share2, FileText, ChevronRight } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface Output {
  _id: string
  output_type: string
  status: string
  confidence_score: number
  flagged: boolean
}

export default function OutputsList() {
  const [outputs] = useState<Output[]>([
    { _id: '1', output_type: 'linkedin', status: 'completed', confidence_score: 0.92, flagged: false },
    { _id: '2', output_type: 'instagram_reel', status: 'completed', confidence_score: 0.88, flagged: false },
    { _id: '3', output_type: 'case_study', status: 'completed', confidence_score: 0.75, flagged: true },
    { _id: '4', output_type: 'instagram_stories', status: 'processing', confidence_score: 0.0, flagged: false },
  ])

  const getOutputConfig = (type: string) => {
    switch (type) {
      case 'linkedin': return { label: 'LinkedIn Post', icon: Share2, color: 'text-blue-400' }
      case 'instagram_reel': return { label: 'Instagram Reel', icon: "/insta.svg", color: 'text-pink-400' }
      case 'instagram_stories': return { label: 'Instagram Stories', icon: "/insta.svg", color: 'text-purple-400' }
      case 'case_study': return { label: 'Case Study', icon: FileText, color: 'text-emerald-400' }
      default: return { label: type, icon: FileCheck, color: 'text-muted-foreground' }
    }
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'completed': return { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' }
      case 'processing': return { color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' }
      default: return { color: 'text-muted-foreground', bg: 'bg-white/5', border: 'border-white/10' }
    }
  }

  return (
    <div className="glass-card border-white/5 rounded-3xl overflow-hidden">
      <div className="p-8 border-b border-white/5 bg-white/2 flex items-center justify-between">
        <h3 className="text-xl font-bold tracking-tight">Active Pipeline Outputs</h3>
        <Badge variant="outline" className="rounded-full bg-white/5 border-white/10">Live Stream</Badge>
      </div>
      <div className="divide-y divide-white/5">
        {outputs.map((output, i) => {
          const config = getOutputConfig(output.output_type);
          const status = getStatusConfig(output.status);
          const Icon = config.icon;

          return (
            <motion.div
              key={output._id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="p-6 hover:bg-white/2 cursor-pointer transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/5 group-hover:scale-110 transition-transform ${config.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-lg">{config.label}</span>
                      {output.flagged && (
                        <Badge variant="outline" className="bg-red-500/10 text-red-400 border-red-500/20 text-[10px] uppercase font-bold py-0">
                          <AlertCircle className="w-3 h-3 mr-1" /> Flagged
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1 flex items-center gap-2">
                      <Activity className="w-3 h-3" />
                      {output.confidence_score > 0
                        ? `Precision: ${(output.confidence_score * 100).toFixed(0)}%`
                        : <span className="animate-pulse flex items-center gap-1">Analyzing media stream...</span>}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <Badge className={`${status.bg} ${status.color} ${status.border} border rounded-xl px-4 py-1.5 text-[10px] uppercase tracking-widest font-black`}>
                    {output.status}
                  </Badge>
                  <ChevronRight className="w-5 h-5 text-muted-foreground/30 group-hover:text-primary transition-colors group-hover:translate-x-1" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  )
}
