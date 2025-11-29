import { Shield, Bell, Settings, Activity, AlertTriangle, FileCheck, Monitor, LogOut, User, Target } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user) return "??";
    const names = user.full_name.split(" ");
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return user.full_name.substring(0, 2).toUpperCase();
  };
  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r border-sidebar-border bg-sidebar text-sidebar-foreground flex flex-col">
        <div className="flex h-16 items-center gap-2 border-b border-sidebar-border px-6">
          <Shield className="h-8 w-8 text-sidebar-primary" />
          <div>
            <h1 className="text-lg font-bold">Cyber HealthGuard</h1>
            <p className="text-xs text-sidebar-foreground/70">AI Security Platform</p>
          </div>
        </div>

        <nav className="space-y-1 p-4 flex-1">
          <NavLink
            to="/dashboard"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent"
            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
          >
            <Activity className="h-5 w-5" />
            Dashboard
          </NavLink>
          
          <NavLink
            to="/alerts"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent"
            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
          >
            <AlertTriangle className="h-5 w-5" />
            Alerts
          </NavLink>
          
          <NavLink
            to="/endpoints"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent"
            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
          >
            <Monitor className="h-5 w-5" />
            Endpoints
          </NavLink>
          
          <NavLink
            to="/compliance"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent"
            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
          >
            <FileCheck className="h-5 w-5" />
            Compliance
          </NavLink>

          <NavLink
            to="/mitre-attack"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent"
            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
          >
            <Target className="h-5 w-5" />
            MITRE ATT&CK
          </NavLink>

          <NavLink
            to="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent"
            activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
          >
            <Settings className="h-5 w-5" />
            Settings
          </NavLink>
        </nav>

        <div className="p-4 border-t border-sidebar-border">
          <div className="rounded-lg bg-sidebar-accent p-3">
            <p className="text-xs text-sidebar-foreground/70 mb-1">Current Organization</p>
            <p className="text-sm font-medium">{user?.organisation_id || 'Not specified'}</p>
            <p className="text-xs text-sidebar-foreground/70 mt-1">Role: {user?.role || 'User'}</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold text-foreground">Security Dashboard</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-critical"></span>
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-medium">
                    {getUserInitials()}
                  </div>
                  <span className="text-sm">{user?.full_name || 'User'}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{user?.full_name}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => window.location.href = '/settings'}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => window.location.href = '/settings'}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
