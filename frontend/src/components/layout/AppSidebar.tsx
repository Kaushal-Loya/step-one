import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { useNavigate, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  FolderOpen,
  Image as ImageIcon,
  BookOpen,
  Home,
  Sparkles,
  Zap,
  Settings
} from "lucide-react"

const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Sessions",
    url: "/sessions",
    icon: FolderOpen,
  },
  {
    title: "Outputs",
    url: "/outputs",
    icon: ImageIcon,
  },
  {
    title: "API Docs",
    url: "/docs",
    icon: BookOpen,
  },
]

export function AppSidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Sidebar className="border-r border-white/5 bg-background/50 backdrop-blur-xl">
      <SidebarHeader className="p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-primary to-blue-600 shadow-lg shadow-primary/25">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-bold tracking-tight">Content Engine</span>
            <span className="text-[10px] uppercase tracking-widest text-primary font-bold">Pro v1.0</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent className="px-3">
        <SidebarGroup>
          <SidebarGroupLabel className="px-3 text-[10px] uppercase tracking-[0.2em] font-bold text-muted-foreground/50 mb-2">Main Console</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="gap-1">
              {items.map((item) => {
                const active = location.pathname === item.url;
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      isActive={active}
                      onClick={() => navigate(item.url)}
                      className={`h-11 rounded-xl px-3 transition-all duration-200 ${active
                          ? "bg-primary/10 text-primary shadow-[inset_0_0_0_1px_rgba(var(--primary-rgb),0.2)]"
                          : "hover:bg-white/5 text-muted-foreground hover:text-foreground"
                        }`}
                    >
                      <item.icon className={`h-5 w-5 ${active ? "text-primary" : ""}`} />
                      <span className="font-medium">{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-4">
          <SidebarGroupLabel className="px-3 text-[10px] uppercase tracking-[0.2em] font-bold text-muted-foreground/50 mb-2">System</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton className="h-11 rounded-xl px-3 text-muted-foreground hover:bg-white/5 hover:text-foreground">
                  <Settings className="h-5 w-5" />
                  <span className="font-medium">Settings</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton className="h-11 rounded-xl px-3 text-muted-foreground hover:bg-white/5 hover:text-foreground">
                  <Zap className="h-5 w-5" />
                  <span className="font-medium">Cluster Logs</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-6">
        <div className="rounded-2xl bg-white/5 p-4 border border-white/5">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold">Node-01 Active</span>
          </div>
          <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
            <div className="h-full w-[45%] bg-primary rounded-full" />
          </div>
          <p className="text-[10px] text-muted-foreground mt-2">GPU Load: 45%</p>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
