import { useState } from 'react'
import { motion } from 'motion/react'
import { Image as ImageIcon, Film, Star, Zap, ChevronRight } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface Asset {
  _id: string
  file_name: string
  file_type: string
  category: string
  aesthetic_score: number
  energy_score: number
}

export default function AssetsList() {
  const [assets] = useState<Asset[]>([
    { _id: '1', file_name: 'IMG_001.jpg', file_type: 'image', category: 'hero', aesthetic_score: 0.85, energy_score: 0.78 },
    { _id: '2', file_name: 'IMG_002.jpg', file_type: 'image', category: 'action', aesthetic_score: 0.72, energy_score: 0.91 },
    { _id: '3', file_name: 'IMG_003.jpg', file_type: 'image', category: 'b_roll', aesthetic_score: 0.68, energy_score: 0.65 },
    { _id: '4', file_name: 'VID_001.mp4', file_type: 'video', category: 'action', aesthetic_score: 0.80, energy_score: 0.88 },
  ])

  const getCategoryConfig = (category: string) => {
    switch (category) {
      case 'hero': return { color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' }
      case 'action': return { color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' }
      case 'b_roll': return { color: 'text-muted-foreground', bg: 'bg-white/5', border: 'border-white/10' }
      default: return { color: 'text-muted-foreground', bg: 'bg-white/5', border: 'border-white/10' }
    }
  }

  return (
    <div className="glass-card border-white/5 rounded-3xl overflow-hidden">
      <div className="p-8 border-b border-white/5 bg-white/2 flex items-center justify-between">
        <h3 className="text-xl font-bold tracking-tight">Ingested Media</h3>
        <Badge variant="outline" className="rounded-full bg-white/5 text-[10px] uppercase tracking-widest font-bold">
          {assets.length} Units
        </Badge>
      </div>
      <div className="divide-y divide-white/5">
        {assets.map((asset, i) => {
          const config = getCategoryConfig(asset.category);
          return (
            <motion.div
              key={asset._id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="p-6 hover:bg-white/2 cursor-pointer transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center border border-white/5 group-hover:scale-110 transition-transform duration-300 shadow-xl shadow-black/20 overflow-hidden relative">
                    <div className="absolute inset-0 bg-linear-to-br from-white/10 to-transparent" />
                    {asset.file_type === 'image' ? (
                      <ImageIcon className="w-6 h-6 text-primary/60 relative z-1" />
                    ) : (
                      <Film className="w-6 h-6 text-blue-400 relative z-1" />
                    )}
                  </div>
                  <div>
                    <div className="font-bold text-lg leading-none mb-2">{asset.file_name}</div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Star className="w-3 h-3 text-yellow-500/70" />
                        Aesthetic: <span className="text-foreground font-bold">{(asset.aesthetic_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-px h-3 bg-white/10" />
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Zap className="w-3 h-3 text-blue-400/70" />
                        Energy: <span className="text-foreground font-bold">{(asset.energy_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <Badge className={`${config.bg} ${config.color} ${config.border} border rounded-xl px-4 py-1.5 text-[10px] uppercase tracking-widest font-black`}>
                    {asset.category}
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
