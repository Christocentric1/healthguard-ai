import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { mockMITREDetections, mockMITREHeatmap } from "@/data/mockMITRE";
import { Shield, AlertTriangle, Activity, Target, TrendingUp, CheckCircle2, Clock } from "lucide-react";
import { format } from "date-fns";

export default function MITREAttack() {
  const activeDetections = mockMITREDetections.filter(d => d.status === 'active');
  const criticalDetections = mockMITREDetections.filter(d => d.threat_assessment.risk_level === 'critical');

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-critical/10 text-critical border-critical',
      high: 'bg-high/10 text-high border-high',
      medium: 'bg-medium/10 text-medium border-medium',
      low: 'bg-low/10 text-low border-low'
    };
    return colors[severity as keyof typeof colors] || '';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'bg-critical/10 text-critical',
      investigating: 'bg-warning/10 text-warning',
      contained: 'bg-info/10 text-info',
      resolved: 'bg-success/10 text-success'
    };
    return colors[status as keyof typeof colors] || '';
  };

  const getTacticColor = (tactic: string) => {
    const colors: { [key: string]: string } = {
      'Initial Access': 'bg-red-500/10 text-red-500',
      'Execution': 'bg-orange-500/10 text-orange-500',
      'Persistence': 'bg-amber-500/10 text-amber-500',
      'Privilege Escalation': 'bg-yellow-500/10 text-yellow-500',
      'Defense Evasion': 'bg-lime-500/10 text-lime-500',
      'Credential Access': 'bg-emerald-500/10 text-emerald-500',
      'Discovery': 'bg-teal-500/10 text-teal-500',
      'Lateral Movement': 'bg-cyan-500/10 text-cyan-500',
      'Collection': 'bg-sky-500/10 text-sky-500',
      'Exfiltration': 'bg-blue-500/10 text-blue-500',
      'Impact': 'bg-purple-500/10 text-purple-500'
    };
    return colors[tactic] || 'bg-muted/50 text-muted-foreground';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">MITRE ATT&CK Threat Intelligence</h1>
          <p className="text-muted-foreground mt-1">Real-time threat detection and attack technique analysis</p>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Detections</CardTitle>
              <AlertTriangle className="h-4 w-4 text-critical" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-critical">{activeDetections.length}</div>
              <p className="text-xs text-muted-foreground">Requires immediate attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Threats</CardTitle>
              <Shield className="h-4 w-4 text-critical" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-critical">{criticalDetections.length}</div>
              <p className="text-xs text-muted-foreground">High-severity incidents</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Unique Techniques</CardTitle>
              <Target className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockMITREHeatmap.length}</div>
              <p className="text-xs text-muted-foreground">Last 30 days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Detections</CardTitle>
              <Activity className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockMITREDetections.length}</div>
              <p className="text-xs text-muted-foreground">All time</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="detections">
          <TabsList>
            <TabsTrigger value="detections">Active Detections</TabsTrigger>
            <TabsTrigger value="heatmap">Technique Heatmap</TabsTrigger>
            <TabsTrigger value="iocs">Indicators of Compromise</TabsTrigger>
          </TabsList>

          {/* Active Detections Tab */}
          <TabsContent value="detections" className="space-y-4 mt-6">
            {mockMITREDetections.map((detection) => (
              <Card key={detection.detection_id} className="border-l-4 border-l-critical">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-critical" />
                        Detection {detection.detection_id}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(detection.timestamp), 'MMM dd, yyyy HH:mm')} UTC • {detection.host} • {detection.user}
                      </p>
                    </div>
                    <Badge className={getStatusColor(detection.status)}>
                      {detection.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* AI Summary */}
                  <div className="bg-muted/50 rounded-lg p-4">
                    <h4 className="font-semibold mb-2">🤖 AI Analysis</h4>
                    <p className="text-sm">{detection.ai_summary.executive_summary}</p>
                  </div>

                  {/* Threat Assessment */}
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-critical" />
                      <div>
                        <p className="text-xs text-muted-foreground">Likelihood</p>
                        <p className="font-semibold">{detection.threat_assessment.likelihood_score}/100</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-critical" />
                      <div>
                        <p className="text-xs text-muted-foreground">Risk Level</p>
                        <Badge className={getSeverityColor(detection.threat_assessment.risk_level)}>
                          {detection.threat_assessment.risk_level}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-success" />
                      <div>
                        <p className="text-xs text-muted-foreground">Confidence</p>
                        <p className="font-semibold">{Math.round(detection.threat_assessment.confidence * 100)}%</p>
                      </div>
                    </div>
                  </div>

                  {/* Detected Techniques */}
                  <div>
                    <h4 className="font-semibold mb-3">Detected MITRE ATT&CK Techniques</h4>
                    <div className="space-y-3">
                      {detection.techniques_detected.map((technique, idx) => (
                        <div key={idx} className="border rounded-lg p-3 space-y-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-semibold">{technique.technique_id} - {technique.technique_name}</p>
                              <p className="text-sm text-muted-foreground">{technique.tactic}</p>
                              {technique.sub_technique && (
                                <p className="text-xs text-muted-foreground">{technique.sub_technique}</p>
                              )}
                            </div>
                            <div className="text-right">
                              <Badge className={getSeverityColor(technique.severity)}>
                                {technique.severity}
                              </Badge>
                              <p className="text-xs text-muted-foreground mt-1">
                                {technique.confidence_score}% confidence
                              </p>
                            </div>
                          </div>
                          <p className="text-sm">{technique.ai_explanation}</p>

                          {/* Indicators */}
                          {technique.indicators.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-semibold mb-1">Indicators:</p>
                              {technique.indicators.map((indicator, i) => (
                                <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1">
                                  [{indicator.indicator_type}] {indicator.indicator_value}
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Recommended Mitigations */}
                          {technique.recommended_mitigations.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-semibold mb-1">Recommended Mitigations:</p>
                              <ul className="text-xs space-y-1">
                                {technique.recommended_mitigations.map((mitigation, i) => (
                                  <li key={i} className="flex gap-2">
                                    <span className="text-primary">•</span>
                                    <span>{mitigation}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* IOCs */}
                  {(detection.iocs.processes.length > 0 || detection.iocs.file_paths.length > 0) && (
                    <div>
                      <h4 className="font-semibold mb-2">Indicators of Compromise</h4>
                      <div className="grid gap-2 md:grid-cols-2">
                        {detection.iocs.processes.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold mb-1">Processes:</p>
                            {detection.iocs.processes.map((proc, i) => (
                              <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1">
                                {proc}
                              </div>
                            ))}
                          </div>
                        )}
                        {detection.iocs.file_paths.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold mb-1">File Paths:</p>
                            {detection.iocs.file_paths.map((path, i) => (
                              <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1">
                                {path}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Heatmap Tab */}
          <TabsContent value="heatmap" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>MITRE ATT&CK Technique Heatmap</CardTitle>
                <p className="text-sm text-muted-foreground">Frequency of detected techniques over the last 30 days</p>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Technique ID</TableHead>
                      <TableHead>Technique Name</TableHead>
                      <TableHead>Tactic</TableHead>
                      <TableHead>Detections</TableHead>
                      <TableHead>Severity</TableHead>
                      <TableHead>Last Detected</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockMITREHeatmap.map((cell) => (
                      <TableRow key={cell.technique_id}>
                        <TableCell className="font-mono text-sm">{cell.technique_id}</TableCell>
                        <TableCell className="font-medium">{cell.technique_name}</TableCell>
                        <TableCell>
                          <Badge className={getTacticColor(cell.tactic)}>
                            {cell.tactic}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <span className="text-lg font-bold">{cell.detection_count}</span>
                        </TableCell>
                        <TableCell>
                          <Badge className={getSeverityColor(cell.severity)}>
                            {cell.severity}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {format(new Date(cell.last_detected), 'MMM dd, HH:mm')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* IOCs Tab */}
          <TabsContent value="iocs" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Consolidated Indicators of Compromise</CardTitle>
                <p className="text-sm text-muted-foreground">All IOCs detected across active threats</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {mockMITREDetections.map((detection) => (
                  <div key={detection.detection_id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold">Detection {detection.detection_id}</h4>
                      <Badge className={getStatusColor(detection.status)}>{detection.status}</Badge>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2">
                      {detection.iocs.ip_addresses.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold mb-1">IP Addresses:</p>
                          {detection.iocs.ip_addresses.map((ip, i) => (
                            <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1">{ip}</div>
                          ))}
                        </div>
                      )}
                      {detection.iocs.domains.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold mb-1">Domains:</p>
                          {detection.iocs.domains.map((domain, i) => (
                            <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1">{domain}</div>
                          ))}
                        </div>
                      )}
                      {detection.iocs.file_hashes.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold mb-1">File Hashes:</p>
                          {detection.iocs.file_hashes.map((hash, i) => (
                            <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1 break-all">{hash}</div>
                          ))}
                        </div>
                      )}
                      {detection.iocs.processes.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold mb-1">Malicious Processes:</p>
                          {detection.iocs.processes.map((proc, i) => (
                            <div key={i} className="text-xs font-mono bg-muted p-2 rounded mt-1">{proc}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
