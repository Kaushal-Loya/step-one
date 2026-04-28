import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { useNavigate, useLocation } from "react-router-dom"
import { Plus, Bell, Search, User } from "lucide-react"

export function AppHeader() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const getPageTitle = () => {
    const path = location.pathname.split('/')[1]
    return path.charAt(0).toUpperCase() + path.slice(1) || 'Home'
  }

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-white/5 px-6 sticky top-0 bg-background/50 backdrop-blur-md z-10">
      <SidebarTrigger className="-ml-1 hover:bg-white/5 rounded-xl" />
      
      <div className="flex-1 flex items-center gap-4">
        <h1 className="text-sm font-semibold tracking-tight text-muted-foreground/80">/ {getPageTitle()}</h1>
        <div className="hidden md:flex relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            placeholder="Search assets or sessions..." 
            className="h-9 w-64 bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 text-xs focus:ring-1 focus:ring-primary outline-none transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="rounded-xl hover:bg-white/5 text-muted-foreground">
          <Bell className="h-5 w-5" />
        </Button>
        <Button onClick={() => navigate('/dashboard')} size="sm" className="rounded-xl shadow-lg shadow-primary/20 hidden sm:flex">
          <Plus className="mr-2 h-4 w-4" />
          New Pipeline
        </Button>
        <div className="h-8 w-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-muted-foreground hover:text-foreground cursor-pointer transition-colors">
          <User className="h-4 w-4" />
        </div>
      </div>
    </header>
  )
}
