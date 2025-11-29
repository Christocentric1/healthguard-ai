import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from '@tanstack/react-query';
import { mockComplianceControls, mockComplianceScores, ComplianceControl } from "@/data/mockData";
import { mockDSPTDomains, mockDSPTScore } from "@/data/mockDSPT";
import { apiFetch, API_ENDPOINTS, USE_MOCK_DATA } from '@/lib/api';
import { Shield, CheckCircle2, XCircle, AlertCircle, Activity, AlertTriangle } from "lucide-react";

export default function Compliance() {
  type Framework = 'hipaa' | 'gdpr' | 'cyber_essentials' | 'cis' | 'iso27001' | 'dspt';

  // Fetch live compliance controls from API
  const { data: complianceData, isLoading } = useQuery({
    queryKey: ['compliance'],
    queryFn: () => apiFetch<ComplianceControl[]>(API_ENDPOINTS.compliance),
    enabled: !USE_MOCK_DATA,
  });

  // Use live data if available, fallback to mock data
  const complianceControls = USE_MOCK_DATA ? mockComplianceControls : (complianceData || mockComplianceControls);

  if (isLoading && !USE_MOCK_DATA) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading compliance data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle2 className="h-5 w-5 text-success" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-critical" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-warning" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      passed: 'bg-success/10 text-success',
      failed: 'bg-critical/10 text-critical',
      warning: 'bg-warning/10 text-warning'
    };
    return colors[status as keyof typeof colors] || '';
  };

  const getFrameworkControls = (framework: Framework) => {
    return complianceControls.filter(c => c.framework === framework);
  };

  const getFrameworkStats = (framework: Framework) => {
    const controls = getFrameworkControls(framework);
    return {
      passed: controls.filter(c => c.status === 'passed').length,
      failed: controls.filter(c => c.status === 'failed').length,
      warning: controls.filter(c => c.status === 'warning').length,
      score: mockComplianceScores[framework]
    };
  };

  const getFrameworkName = (framework: Framework) => {
    const names = {
      hipaa: 'HIPAA',
      gdpr: 'GDPR',
      cyber_essentials: 'Cyber Essentials',
      cis: 'CIS Controls',
      iso27001: 'ISO 27001',
      dspt: 'DSPT'
    };
    return names[framework];
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Compliance Dashboard</h1>
          <p className="text-muted-foreground mt-1">Multi-framework compliance monitoring</p>
        </div>

        <Tabs defaultValue="hipaa">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="hipaa">HIPAA</TabsTrigger>
            <TabsTrigger value="gdpr">GDPR</TabsTrigger>
            <TabsTrigger value="cyber_essentials">Cyber Essentials</TabsTrigger>
            <TabsTrigger value="cis">CIS Controls</TabsTrigger>
            <TabsTrigger value="iso27001">ISO 27001</TabsTrigger>
            <TabsTrigger value="dspt">DSPT</TabsTrigger>
          </TabsList>

          {(['hipaa', 'gdpr', 'cyber_essentials', 'cis', 'iso27001', 'dspt'] as const).map((framework) => {
            const stats = getFrameworkStats(framework);
            const controls = getFrameworkControls(framework);
            return (
              <TabsContent key={framework} value={framework} className="space-y-6 mt-6">

                <div className="grid gap-6 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5 text-primary" />
                        Overall Compliance Score
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-center">
                          <div className="relative h-40 w-40">
                            <svg className="h-40 w-40 transform -rotate-90">
                              <circle
                                cx="80"
                                cy="80"
                                r="70"
                                stroke="currentColor"
                                strokeWidth="12"
                                fill="transparent"
                                className="text-muted"
                              />
                              <circle
                                cx="80"
                                cy="80"
                                r="70"
                                stroke="currentColor"
                                strokeWidth="12"
                                fill="transparent"
                                strokeDasharray={`${2 * Math.PI * 70}`}
                                strokeDashoffset={`${2 * Math.PI * 70 * (1 - stats.score / 100)}`}
                                className="text-success"
                                strokeLinecap="round"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-4xl font-bold">{stats.score}%</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-muted-foreground">
                            Your organization meets {stats.score}% of {getFrameworkName(framework)} requirements
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Control Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <CheckCircle2 className="h-5 w-5 text-success" />
                            <span className="text-sm">Passed Controls</span>
                          </div>
                          <span className="text-2xl font-bold text-success">{stats.passed}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <XCircle className="h-5 w-5 text-critical" />
                            <span className="text-sm">Failed Controls</span>
                          </div>
                          <span className="text-2xl font-bold text-critical">{stats.failed}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <AlertCircle className="h-5 w-5 text-warning" />
                            <span className="text-sm">Warning Controls</span>
                          </div>
                          <span className="text-2xl font-bold text-warning">{stats.warning}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Compliance Controls</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[50px]"></TableHead>
                          <TableHead>Control ID</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Description</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Remediation</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {controls.map((control) => (
                          <TableRow key={control.id}>
                            <TableCell>
                              {getStatusIcon(control.status)}
                            </TableCell>
                            <TableCell className="font-mono text-sm">{control.control_id}</TableCell>
                            <TableCell className="font-medium">{control.name}</TableCell>
                            <TableCell className="text-sm text-muted-foreground max-w-md">
                              {control.description}
                            </TableCell>
                            <TableCell>
                              <Badge className={getStatusColor(control.status)}>
                                {control.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-sm max-w-xs">
                              {control.remediation || <span className="text-muted-foreground">—</span>}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>
            );
          })}
        </Tabs>
      </div>
    </Layout>
  );
}
