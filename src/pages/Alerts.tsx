import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from '@tanstack/react-query';
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { mockAlerts, Alert } from "@/data/mockData";
import { fetchAlerts, USE_MOCK_DATA } from '@/lib/api';
import { Filter, Activity } from "lucide-react";

export default function Alerts() {
  const navigate = useNavigate();
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Fetch live alerts from API
  const { data: alertsData, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: fetchAlerts,
    enabled: !USE_MOCK_DATA,
  });

  // Use live data if available, fallback to mock data
  const alerts = USE_MOCK_DATA ? mockAlerts : (alertsData?.alerts || mockAlerts);

  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter !== "all" && alert.severity !== severityFilter) return false;
    if (statusFilter !== "all" && alert.status !== statusFilter) return false;
    return true;
  });

  if (isLoading && !USE_MOCK_DATA) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading alerts...</p>
          </div>
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

  const getStatusColor = (status: string) => {
    const colors = {
      new: 'bg-critical/10 text-critical',
      investigating: 'bg-warning/10 text-warning',
      resolved: 'bg-success/10 text-success',
      false_positive: 'bg-muted/10 text-muted-foreground'
    };
    return colors[status as keyof typeof colors] || '';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Security Alerts</h1>
            <p className="text-muted-foreground mt-1">Monitor and manage security incidents</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>All Alerts</CardTitle>
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Select value={severityFilter} onValueChange={setSeverityFilter}>
                  <SelectTrigger className="w-[130px]">
                    <SelectValue placeholder="Severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Severity</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[130px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="investigating">Investigating</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                    <SelectItem value="false_positive">False Positive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alert ID</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Host</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAlerts.map((alert) => (
                  <TableRow key={alert.id} className="cursor-pointer hover:bg-muted/50">
                    <TableCell className="font-medium">{alert.id}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(alert.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>{alert.host}</TableCell>
                    <TableCell>{alert.category}</TableCell>
                    <TableCell>
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className={`font-semibold ${alert.ai_risk_score >= 80 ? 'text-critical' : alert.ai_risk_score >= 60 ? 'text-warning' : 'text-success'}`}>
                        {alert.ai_risk_score}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(alert.status)}>
                        {alert.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => navigate(`/alerts/${alert.id}`)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
