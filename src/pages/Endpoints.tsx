import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useQuery } from '@tanstack/react-query';
import { mockEndpoints, Endpoint } from "@/data/mockData";
import { apiFetch, API_ENDPOINTS, USE_MOCK_DATA } from '@/lib/api';
import { Activity } from "lucide-react";

export default function Endpoints() {
  // Fetch live endpoints from API
  const { data: endpointsData, isLoading } = useQuery({
    queryKey: ['endpoints'],
    queryFn: () => apiFetch<{endpoints: Endpoint[], total: number}>(API_ENDPOINTS.endpoints),
    enabled: !USE_MOCK_DATA,
  });

  // Use live data if available, fallback to mock data
  const endpoints = USE_MOCK_DATA ? mockEndpoints : (endpointsData?.endpoints || mockEndpoints);

  if (isLoading && !USE_MOCK_DATA) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading endpoints...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const getSeverityColor = (level: string) => {
    const colors = {
      critical: 'bg-critical/10 text-critical border-critical/20',
      high: 'bg-high/10 text-high border-high/20',
      medium: 'bg-medium/10 text-medium border-medium/20',
      low: 'bg-low/10 text-low border-low/20'
    };
    return colors[level as keyof typeof colors] || '';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      online: 'bg-success/10 text-success',
      offline: 'bg-muted/10 text-muted-foreground',
      warning: 'bg-warning/10 text-warning'
    };
    return colors[status as keyof typeof colors] || '';
  };

  const formatLastSeen = (timestamp: string) => {
    const now = Date.now();
    const then = new Date(timestamp).getTime();
    const diff = now - then;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Endpoints</h1>
          <p className="text-muted-foreground mt-1">Monitor all devices in your network</p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Endpoints</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{endpoints.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Online</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {endpoints.filter(e => e.status === 'online').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Warnings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">
                {endpoints.filter(e => e.status === 'warning').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Offline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-muted-foreground">
                {endpoints.filter(e => e.status === 'offline').length}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>All Endpoints</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Hostname</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Operating System</TableHead>
                  <TableHead>Last Seen</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {endpoints.map((endpoint) => (
                  <TableRow key={endpoint.id}>
                    <TableCell className="font-medium">{endpoint.hostname}</TableCell>
                    <TableCell className="font-mono text-sm">{endpoint.ip}</TableCell>
                    <TableCell>{endpoint.os}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatLastSeen(endpoint.last_seen)}
                    </TableCell>
                    <TableCell>
                      <Badge className={getSeverityColor(endpoint.risk_level)}>
                        {endpoint.risk_level}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(endpoint.status)}>
                        {endpoint.status}
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
