import { useParams, useNavigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { mockAlerts } from "@/data/mockData";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";

export default function AlertDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const alert = mockAlerts.find(a => a.id === id);
  const [status, setStatus] = useState<string>(alert?.status || 'new');

  if (!alert) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold">Alert not found</h2>
          <Button onClick={() => navigate('/alerts')} className="mt-4">
            Back to Alerts
          </Button>
        </div>
      </Layout>
    );
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-critical/10 text-critical border-critical/20',
      high: 'bg-high/10 text-high border-high/20',
      medium: 'bg-medium/10 text-medium border-medium/20',
      low: 'bg-low/10 text-low border-low/20'
    };
    return colors[severity as keyof typeof colors] || '';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/alerts')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Alert Details</h1>
            <p className="text-muted-foreground mt-1">{alert.id}</p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Alert Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Category</p>
                <p className="font-medium">{alert.category}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Severity</p>
                <Badge className={getSeverityColor(alert.severity)}>
                  {alert.severity}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">AI Risk Score</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${alert.ai_risk_score >= 80 ? 'bg-critical' : alert.ai_risk_score >= 60 ? 'bg-warning' : 'bg-success'}`}
                      style={{ width: `${alert.ai_risk_score}%` }}
                    />
                  </div>
                  <span className="font-semibold">{alert.ai_risk_score}/100</span>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Timestamp</p>
                <p className="font-medium">{new Date(alert.timestamp).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Source</p>
                <p className="font-medium">{alert.source}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Affected Resources</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Host</p>
                <p className="font-medium">{alert.host}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">User</p>
                <p className="font-medium">{alert.user}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Organisation ID</p>
                <p className="font-medium">{alert.organisation_id}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Status</p>
                <Select value={status} onValueChange={setStatus}>
                  <SelectTrigger className="w-[200px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="investigating">Investigating</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                    <SelectItem value="false_positive">False Positive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-foreground">{alert.description}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recommended Action</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-foreground">{alert.recommended_action}</p>
            <div className="flex gap-2 mt-4">
              <Button>Take Action</Button>
              <Button variant="outline">Add to Incident</Button>
              <Button variant="outline">Export Report</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
