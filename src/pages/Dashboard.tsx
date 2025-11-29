import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Shield, Activity, FileCheck, FileWarning, Brain, Server, TrendingUp, AlertCircle } from "lucide-react";
import { useQuery } from '@tanstack/react-query';
import { apiFetch, API_ENDPOINTS, USE_MOCK_DATA } from '@/lib/api';
import {
  mockAlerts,
  mockComplianceScore,
  mockFileIntegrityEvents,
  mockAIInsights,
  mockAISummary,
  mockEndpointHealth,
  mockHighRiskEndpoints,
  Alert
} from "@/data/mockData";
import { format } from "date-fns";

export default function Dashboard() {
  // Fetch live alerts from API
  const { data: alertsData, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => apiFetch<{alerts: Alert[], total: number}>(API_ENDPOINTS.alerts),
    enabled: !USE_MOCK_DATA,
  });

  // Use live data if available, fallback to mock data
  const alerts = USE_MOCK_DATA ? mockAlerts : (alertsData?.alerts || mockAlerts);

  const todayAlerts = alerts.length;
  const criticalAlerts = alerts.filter(a => a.severity === 'critical' && a.status !== 'resolved').length;
  const riskScore = 72;
  const fimFlaggedEvents = mockFileIntegrityEvents.filter(e => e.status === 'flagged').length;

  // Show loading state
  if (alertsLoading && !USE_MOCK_DATA) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading dashboard data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-critical/10 text-critical',
      high: 'bg-high/10 text-high',
      medium: 'bg-medium/10 text-medium',
      low: 'bg-low/10 text-low'
    };
    return colors[severity as keyof typeof colors] || '';
  };

  const getActionColor = (action: string) => {
    const colors = {
      created: 'bg-blue-500/10 text-blue-500',
      modified: 'bg-warning/10 text-warning',
      deleted: 'bg-critical/10 text-critical',
      accessed: 'bg-muted/10 text-muted-foreground'
    };
    return colors[action as keyof typeof colors] || '';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Overview of your security posture</p>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Alerts Today</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{todayAlerts}</div>
              <p className="text-xs text-muted-foreground">
                +2 from yesterday
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-critical" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-critical">{criticalAlerts}</div>
              <p className="text-xs text-muted-foreground">
                Requires immediate attention
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-high">{riskScore}/100</div>
              <p className="text-xs text-muted-foreground">
                Medium risk level
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <FileCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">{mockComplianceScore}%</div>
              <p className="text-xs text-muted-foreground">
                Multi-framework
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">FIM Events</CardTitle>
              <FileWarning className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">{fimFlaggedEvents}</div>
              <p className="text-xs text-muted-foreground">
                Flagged for review
              </p>
            </CardContent>
          </Card>
        </div>

        {/* AI Security Analyst Summary Panel */}
        <Card className="border-l-4 border-l-purple-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-500" />
              AI Security Analyst Summary
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Last updated: {format(new Date(mockAISummary.last_updated), 'yyyy-MM-dd HH:mm')} UTC
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Alerts (24h)</p>
                <p className="text-2xl font-bold">{mockAISummary.alerts_24h}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Critical Incidents</p>
                <p className="text-2xl font-bold text-critical">{mockAISummary.critical_incidents}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Threats Mitigated</p>
                <p className="text-2xl font-bold text-success">{mockAISummary.threats_mitigated}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Avg Response Time</p>
                <p className="text-2xl font-bold">{mockAISummary.average_response_time}</p>
              </div>
            </div>

            {/* AI Detection Insights */}
            <div>
              <h4 className="text-sm font-semibold mb-3">🔍 Detection Insights & Correlations</h4>
              <div className="space-y-2">
                {mockAIInsights.map((insight) => (
                  <div
                    key={insight.id}
                    className={`flex items-start gap-3 p-3 rounded-lg border ${
                      insight.severity === 'critical'
                        ? 'bg-critical/5 border-critical/20'
                        : insight.severity === 'high'
                        ? 'bg-high/5 border-high/20'
                        : 'bg-muted/50 border-border'
                    }`}
                  >
                    <AlertCircle
                      className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                        insight.severity === 'critical'
                          ? 'text-critical'
                          : insight.severity === 'high'
                          ? 'text-high'
                          : 'text-warning'
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">{insight.insight}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Affected: {insight.affected_count} {insight.affected_count === 1 ? 'entity' : 'entities'}
                      </p>
                    </div>
                    <Badge className={getSeverityColor(insight.severity)}>
                      {insight.severity}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Actions */}
            <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-blue-500" />
                Recommended Actions
              </h4>
              <ol className="space-y-2 text-sm">
                {mockAISummary.recommended_actions.map((action, index) => (
                  <li key={index} className="flex gap-2">
                    <span className="font-semibold text-blue-500">{index + 1}.</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ol>
            </div>
          </CardContent>
        </Card>

        {/* Endpoint Overview Panel */}
        <Card className="border-l-4 border-l-cyan-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5 text-cyan-500" />
              Endpoint Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Total Endpoints</p>
                <p className="text-2xl font-bold">{mockEndpointHealth.total_endpoints}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Online</p>
                <p className="text-2xl font-bold text-success">{mockEndpointHealth.online}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Offline</p>
                <p className="text-2xl font-bold text-muted-foreground">{mockEndpointHealth.offline}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">At Risk</p>
                <p className="text-2xl font-bold text-high">{mockEndpointHealth.at_risk}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Outdated Patches</p>
                <p className="text-2xl font-bold text-warning">{mockEndpointHealth.outdated_patches}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">High Risk</p>
                <p className="text-2xl font-bold text-critical">{mockEndpointHealth.high_risk_count}</p>
              </div>
            </div>

            {/* Top 5 Endpoints Requiring Attention */}
            <div>
              <h4 className="text-sm font-semibold mb-3">⚠️ Top 5 Endpoints Requiring Attention</h4>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Hostname</TableHead>
                    <TableHead>Risk Level</TableHead>
                    <TableHead>Issue Detected</TableHead>
                    <TableHead>Last Seen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockHighRiskEndpoints.map((endpoint) => (
                    <TableRow key={endpoint.hostname}>
                      <TableCell className="font-mono text-sm font-medium">
                        {endpoint.hostname}
                      </TableCell>
                      <TableCell>
                        <Badge className={getSeverityColor(endpoint.risk_level)}>
                          {endpoint.risk_level}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm max-w-md">
                        {endpoint.issue}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {format(new Date(endpoint.last_seen), 'MMM dd, HH:mm')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Overall Health Summary */}
            <div className="bg-muted/50 rounded-lg p-3 text-center">
              <p className="text-sm">
                <span className="font-semibold">Overall Endpoint Health: </span>
                <span className={
                  mockEndpointHealth.high_risk_count > 10 ? 'text-critical' :
                  mockEndpointHealth.at_risk > 20 ? 'text-warning' :
                  'text-success'
                }>
                  {mockEndpointHealth.high_risk_count > 10 ? 'Critical' :
                   mockEndpointHealth.at_risk > 20 ? 'Moderate' :
                   'Good'}
                </span>
                {' '}— {Math.round((mockEndpointHealth.online / mockEndpointHealth.total_endpoints) * 100)}% endpoints online,
                {' '}{mockEndpointHealth.high_risk_count} requiring immediate attention
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Recent Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="flex items-start justify-between border-b border-border pb-4 last:border-0 last:pb-0">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`inline-block h-2 w-2 rounded-full bg-${alert.severity}`}></span>
                      <p className="font-medium">{alert.category}</p>
                      <span className="text-xs text-muted-foreground">{alert.id}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.description}</p>
                    <p className="text-xs text-muted-foreground">Host: {alert.host} • User: {alert.user}</p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    alert.status === 'new' ? 'bg-critical/10 text-critical' :
                    alert.status === 'investigating' ? 'bg-warning/10 text-warning' :
                    'bg-success/10 text-success'
                  }`}>
                    {alert.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* File Integrity Monitoring */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileWarning className="h-5 w-5 text-warning" />
              File Integrity Monitoring
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>File Path</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockFileIntegrityEvents.slice(0, 5).map((event) => (
                  <TableRow key={event.id}>
                    <TableCell className="text-sm">
                      {format(new Date(event.timestamp), 'MMM dd, HH:mm')}
                    </TableCell>
                    <TableCell className="font-mono text-sm max-w-xs truncate">
                      {event.file_path}
                    </TableCell>
                    <TableCell>
                      <Badge className={getActionColor(event.action)}>
                        {event.action}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">{event.user}</TableCell>
                    <TableCell>
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={event.status === 'flagged' ? 'destructive' : 'outline'}>
                        {event.status}
                      </Badge>
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
