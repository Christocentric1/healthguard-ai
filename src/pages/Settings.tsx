import { useState } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { useTheme } from "@/contexts/ThemeContext";
import { Check } from "lucide-react";

export default function Settings() {
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();
  const [criticalAlerts, setCriticalAlerts] = useState(true);
  const [dailySummary, setDailySummary] = useState(true);
  const [highAlerts, setHighAlerts] = useState(false);
  const [email, setEmail] = useState("alice.smith@riverside-medical.nhs");

  const themes = [
    { id: 'blue', name: 'Blue', color: 'bg-[hsl(215,70%,25%)]' },
    { id: 'black', name: 'Black', color: 'bg-[hsl(0,0%,10%)]' },
    { id: 'green', name: 'Green', color: 'bg-[hsl(145,70%,25%)]' },
    { id: 'purple', name: 'Purple', color: 'bg-[hsl(275,70%,30%)]' },
  ] as const;

  const handleSave = () => {
    toast({
      title: "Settings saved",
      description: "Your notification preferences have been updated.",
    });
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-3xl">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-1">Manage your account and notification preferences</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>
              Customize the look and feel of your security dashboard
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="mb-3 block">Theme Color</Label>
              <div className="grid grid-cols-4 gap-3">
                {themes.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    className={`relative flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-all hover:shadow-md ${
                      theme === t.id ? 'border-primary' : 'border-border'
                    }`}
                  >
                    <div className={`h-12 w-12 rounded-full ${t.color} relative`}>
                      {theme === t.id && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Check className="h-6 w-6 text-white" />
                        </div>
                      )}
                    </div>
                    <span className="text-sm font-medium">{t.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Email Notifications</CardTitle>
            <CardDescription>
              Configure which alerts you want to receive via email
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="critical">Critical Alerts</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive immediate notifications for critical security alerts
                  </p>
                </div>
                <Switch
                  id="critical"
                  checked={criticalAlerts}
                  onCheckedChange={setCriticalAlerts}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="high">High Priority Alerts</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications for high priority alerts
                  </p>
                </div>
                <Switch
                  id="high"
                  checked={highAlerts}
                  onCheckedChange={setHighAlerts}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="daily">Daily Summary</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive a daily summary of all security events
                  </p>
                </div>
                <Switch
                  id="daily"
                  checked={dailySummary}
                  onCheckedChange={setDailySummary}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>
              Your role and organization details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Organization</p>
              <p className="font-medium">Riverside Medical Centre</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Role</p>
              <p className="font-medium">Analyst</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">User ID</p>
              <p className="font-medium font-mono">USR-2024-001</p>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button onClick={handleSave}>Save Changes</Button>
        </div>
      </div>
    </Layout>
  );
}
