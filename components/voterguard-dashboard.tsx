'use client'

import { useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  BookOpenCheck,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  CloudOff,
  Database,
  FileBarChart,
  FileClock,
  FileSearch,
  Filter,
  Fingerprint,
  Flag,
  FolderSearch,
  Gauge,
  Image as ImageIcon,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  MoreHorizontal,
  Network,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Upload,
  UserRound,
  UsersRound,
  Wifi,
  X,
} from 'lucide-react'

const navItems = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Image Verification', icon: ImageIcon },
  { label: 'Duplicate Detection', icon: Fingerprint },
  { label: 'Registration Integrity', icon: ClipboardCheck },
  { label: 'Investigation Centre', icon: FolderSearch, count: 12 },
  { label: 'Officer Monitoring', icon: UsersRound },
  { label: 'Audit Logs', icon: FileClock },
  { label: 'Reports & Analytics', icon: FileBarChart },
  { label: 'Synchronisation', icon: Network },
  { label: 'Settings', icon: Settings },
]

const records = [
  { id: 'VG-2026-00841', location: 'Lagos Mainland · Ward 04', reason: 'Image mismatch indicators', risk: 'High', status: 'Awaiting review', time: '12 min ago' },
  { id: 'VG-2026-00837', location: 'Kano Municipal · Ward 11', reason: 'Duplicate photograph match', risk: 'Medium', status: 'Assigned', time: '34 min ago' },
  { id: 'VG-2026-00829', location: 'Abuja Municipal · Ward 02', reason: 'Incomplete registration data', risk: 'Low', status: 'In review', time: '1 hr ago' },
  { id: 'VG-2026-00821', location: 'Rivers East · Ward 08', reason: 'Unusual submission pattern', risk: 'Medium', status: 'Awaiting review', time: '2 hrs ago' },
]

const activityItems = [
  ['Photograph uploaded', 'Officer NG-042 · Lagos Mainland', '2 min ago', 'upload'],
  ['Case assigned', 'INV-00218 assigned to A. Okafor', '18 min ago', 'case'],
  ['Record flagged', 'VG-2026-00841 · Image integrity', '32 min ago', 'flag'],
  ['Report generated', 'Weekly integrity summary · 04 Nov', '1 hr ago', 'report'],
]

function statusClass(value: string) {
  if (value === 'High') return 'risk-high'
  if (value === 'Medium') return 'risk-medium'
  if (value === 'Low') return 'risk-low'
  return 'status-neutral'
}

function MetricCard({ label, value, change, icon: Icon, tone }: { label: string; value: string; change: string; icon: typeof Activity; tone: string }) {
  const positive = change.startsWith('+')
  return (
    <div className="metric-card">
      <div className="metric-top"><span className={`metric-icon ${tone}`}><Icon /></span><span className={positive ? 'metric-change positive' : 'metric-change negative'}>{positive ? <ArrowUpRight /> : <ArrowDownRight />}{change}</span></div>
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  )
}

function Overview({ onOpenRecord }: { onOpenRecord: (id: string) => void }) {
  const [riskFilter, setRiskFilter] = useState('All risk levels')
  const filteredRecords = useMemo(() => riskFilter === 'All risk levels' ? records : records.filter((record) => record.risk === riskFilter), [riskFilter])
  return (
    <div className="view-stack">
      <div className="page-heading"><div><div className="eyebrow">Command centre / Overview</div><h1>Integrity overview</h1><p>Monitor registration quality and review signals across the national exercise.</p></div><div className="heading-actions"><button className="secondary-button"><CalendarDays /> 01 Nov – 05 Nov 2026 <ChevronDown /></button><button className="primary-button"><FileBarChart /> Generate report</button></div></div>
      <div className="demo-banner"><Sparkles /><div><strong>Demonstration environment</strong><span>All records, metrics and outcomes shown are synthetic prototype data. No live voter information is connected.</span></div><button aria-label="Dismiss"><X /></button></div>
      <div className="metric-grid">
        <MetricCard label="Total records analysed" value="1,284,560" change="+8.4%" icon={Database} tone="blue" />
        <MetricCard label="Successfully verified" value="1,249,782" change="+6.8%" icon={ShieldCheck} tone="green" />
        <MetricCard label="Suspicious records flagged" value="8,421" change="-2.1%" icon={Flag} tone="red" />
        <MetricCard label="Awaiting investigation" value="2,184" change="+12.4%" icon={FolderSearch} tone="amber" />
      </div>
      <div className="chart-grid"><div className="panel activity-panel"><div className="panel-header"><div><h2>Registration activity</h2><p>Records processed across all monitored zones</p></div><button className="icon-button"><MoreHorizontal /></button></div><div className="chart-legend"><span><i className="legend-dot navy" /> Records processed</span><span><i className="legend-dot red" /> Flagged</span></div><div className="line-chart"><div className="y-labels"><span>320k</span><span>240k</span><span>160k</span><span>80k</span><span>0</span></div><div className="chart-area"><div className="grid-lines"><i /><i /><i /><i /><i /></div><svg viewBox="0 0 700 220" preserveAspectRatio="none" aria-label="Registration activity line chart"><path d="M0,176 C38,170 48,145 78,151 S128,106 163,129 S217,148 247,104 S291,124 322,91 S367,82 398,100 S435,74 471,84 S514,42 549,63 S588,80 622,45 S664,55 700,25" fill="none" stroke="#12395b" strokeWidth="3" /><path d="M0,193 C45,198 64,180 92,186 S140,166 171,179 S218,172 249,183 S295,157 329,171 S371,160 404,169 S450,140 479,158 S526,130 558,144 S607,119 638,131 S675,111 700,120" fill="none" stroke="#c74b4b" strokeWidth="2" strokeDasharray="5 5" /></svg><div className="x-labels"><span>01 Nov</span><span>02 Nov</span><span>03 Nov</span><span>04 Nov</span><span>05 Nov</span></div></div></div></div><div className="panel risk-panel"><div className="panel-header"><div><h2>Risk distribution</h2><p>Current classification of analysed records</p></div><button className="icon-button"><MoreHorizontal /></button></div><div className="donut-wrap"><div className="donut"><div className="donut-center"><strong>1.28M</strong><span>records</span></div></div><div className="risk-list"><div><span><i className="legend-dot green" /> Verified</span><strong>97.3%</strong></div><div><span><i className="legend-dot amber" /> Needs review</span><strong>1.7%</strong></div><div><span><i className="legend-dot red" /> High risk</span><strong>0.7%</strong></div><div><span><i className="legend-dot grey" /> Incomplete</span><strong>0.3%</strong></div></div></div></div></div>
      <div className="lower-grid"><div className="panel table-panel"><div className="panel-header"><div><h2>Recent flagged records</h2><p>Priority cases requiring administrator attention</p></div><button className="text-button">View all <ChevronRight /></button></div><div className="table-toolbar"><div className="table-search"><Search /><input placeholder="Search records" /></div><select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)} aria-label="Filter by risk level"><option>All risk levels</option><option>High</option><option>Medium</option><option>Low</option></select><button className="filter-button"><Filter /> Filters</button></div><div className="table-scroll"><table><thead><tr><th>Record ID</th><th>Location</th><th>Flag reason</th><th>Risk</th><th>Status</th><th /></tr></thead><tbody>{filteredRecords.map((record) => <tr key={record.id}><td><button className="record-link" onClick={() => onOpenRecord(record.id)}>{record.id}</button><small>{record.time}</small></td><td>{record.location}</td><td>{record.reason}</td><td><span className={`risk-pill ${statusClass(record.risk)}`}>{record.risk}</span></td><td><span className="status-text"><i />{record.status}</span></td><td><button className="row-action" onClick={() => onOpenRecord(record.id)} aria-label={`Open ${record.id}`}><ChevronRight /></button></td></tr>)}</tbody></table></div></div><div className="panel activity-list"><div className="panel-header"><div><h2>Administrative activity</h2><p>Latest actions across the command centre</p></div><button className="icon-button"><MoreHorizontal /></button></div><div className="activity-items">{activityItems.map(([title, detail, time, type]) => <div className="activity-item" key={title}><span className={`activity-icon ${type}`}>{type === 'upload' ? <Upload /> : type === 'case' ? <BriefcaseBusiness /> : type === 'flag' ? <Flag /> : <FileBarChart />}</span><div><strong>{title}</strong><p>{detail}</p><span>{time}</span></div></div>)}</div></div></div>
    </div>
  )
}

function ImageVerification() {
  const [fileName, setFileName] = useState('')
  return <div className="view-stack"><div className="page-heading"><div><div className="eyebrow">Verification / Image integrity</div><h1>Image verification</h1><p>Examine registration photographs for quality and integrity indicators.</p></div><span className="prototype-chip"><Sparkles /> Demonstration feature</span></div><div className="notice-card"><CircleHelp /><div><strong>Human review is always required</strong><p>Automated image authenticity analysis may produce false positives. Results are decision-support signals, not conclusive proof of fraud or identity.</p></div></div><div className="verification-grid"><div className="panel upload-panel"><div className="panel-header"><div><h2>Upload photograph</h2><p>Use a synthetic record for this prototype</p></div><span className="step-number">01</span></div><label className="upload-zone"><input type="file" accept="image/*" onChange={(e) => setFileName(e.target.files?.[0]?.name ?? '')} /><span className="upload-symbol"><Upload /></span><strong>{fileName || 'Drop a photograph here'}</strong><span>{fileName ? 'Ready for demonstration analysis' : 'or click to browse · JPEG, PNG up to 10MB'}</span></label><div className="metadata"><div><span>Record reference</span><strong>VG-DEMO-00482</strong></div><div><span>Capture source</span><strong>Registration desk · Abuja</strong></div><div><span>Submission date</span><strong>05 Nov 2026, 09:42</strong></div></div><button className="primary-button full-button" onClick={() => setFileName(fileName || 'synthetic-voter-photo.jpg')}><ShieldCheck /> Run demonstration analysis</button></div><div className="panel results-panel"><div className="panel-header"><div><h2>Integrity assessment</h2><p>Simulated output for training purposes</p></div><span className="status-badge pending">Awaiting image</span></div><div className="empty-result"><span><ImageIcon /></span><strong>No analysis run</strong><p>Upload a synthetic photograph to view simulated indicators. This prototype does not perform biometric verification or AI detection.</p></div><div className="assessment-foot"><LockKeyhole /> Analysis remains local to this demonstration interface.</div></div></div></div>
}

function GenericModule({ title, eyebrow, description, icon: Icon, kind }: { title: string; eyebrow: string; description: string; icon: typeof Activity; kind: string }) {
  const [activeTab, setActiveTab] = useState('All records')
  const [showModal, setShowModal] = useState(false)
  return <div className="view-stack"><div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div><button className="primary-button" onClick={() => setShowModal(true)}><Icon /> New {kind}</button></div><div className="module-summary"><div className="module-icon"><Icon /></div><div><strong>{kind} workspace</strong><span>Structured review tools with synthetic records for demonstration.</span></div><span className="prototype-chip"><Sparkles /> Prototype mode</span></div><div className="panel module-panel"><div className="tabs">{['All records', 'Needs review', 'In progress', 'Resolved'].map((tab) => <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => setActiveTab(tab)}>{tab}<span>{tab === 'All records' ? '48' : tab === 'Needs review' ? '12' : tab === 'In progress' ? '24' : '12'}</span></button>)}</div><div className="module-toolbar"><div className="table-search"><Search /><input placeholder={`Search ${kind.toLowerCase()}...`} /></div><button className="secondary-button"><SlidersHorizontal /> Filters</button><button className="secondary-button"><DownloadIcon /> Export</button></div><div className="record-list">{['VG-2026-00841', 'INV-00218', 'VG-2026-00796', 'VG-2026-00774'].map((id, index) => <div className="record-row" key={id}><span className={`row-icon ${index === 0 ? 'red' : index === 1 ? 'amber' : 'blue'}`}><Icon /></span><div className="row-main"><strong>{id}</strong><span>{kind === 'investigation' ? ['Image integrity indicators', 'Duplicate image comparison', 'Missing registration information', 'Unusual submission pattern'][index] : 'Synthetic record · Abuja Municipal Ward 02'}</span></div><span className={`risk-pill ${index === 0 ? 'risk-high' : index === 1 ? 'risk-medium' : 'risk-low'}`}>{index === 0 ? 'High' : index === 1 ? 'Medium' : 'Low'}</span><span className="status-text"><i />{index === 0 ? 'Needs review' : 'In progress'}</span><button className="row-action" onClick={() => setShowModal(true)}><ChevronRight /></button></div>)}</div></div>{showModal && <div className="modal-backdrop" role="presentation" onClick={() => setShowModal(false)}><div className="modal-card" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}><div className="modal-header"><div><div className="eyebrow">Simulated record</div><h2>Review {kind}</h2></div><button className="icon-button" onClick={() => setShowModal(false)}><X /></button></div><div className="modal-body"><div className="modal-id">VG-2026-00841</div><p>This evidence bundle is synthetic demonstration data. No real voter database or biometric matching service is connected.</p><div className="evidence-grid"><div><span>Risk classification</span><strong className="text-red">High · requires human review</strong></div><div><span>Assigned reviewer</span><strong>A. Okafor</strong></div><div><span>Last activity</span><strong>05 Nov 2026, 10:22</strong></div><div><span>Evidence items</span><strong>4 synthetic artifacts</strong></div></div></div><div className="modal-footer"><button className="secondary-button" onClick={() => setShowModal(false)}>Close</button><button className="primary-button" onClick={() => setShowModal(false)}><Check /> Mark for review</button></div></div></div>}</div>
}

function DownloadIcon() { return <ArrowDownRight /> }

export default function VoterGuardDashboard() {
  const [active, setActive] = useState('Overview')
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [recordOpen, setRecordOpen] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const page = active === 'Overview' ? <Overview onOpenRecord={setRecordOpen} /> : active === 'Image Verification' ? <ImageVerification /> : active === 'Duplicate Detection' ? <GenericModule title="Duplicate detection" eyebrow="Verification / Photograph comparison" description="Compare registration photographs and review simulated similarity indicators." icon={Fingerprint} kind="comparison" /> : active === 'Registration Integrity' ? <GenericModule title="Registration integrity" eyebrow="Records / Quality assurance" description="Examine registration records for completeness, consistency and risk signals." icon={ClipboardCheck} kind="record" /> : active === 'Investigation Centre' ? <GenericModule title="Investigation centre" eyebrow="Cases / Review queue" description="Coordinate flagged cases with clear evidence trails and accountable outcomes." icon={FolderSearch} kind="investigation" /> : active === 'Officer Monitoring' ? <GenericModule title="Officer monitoring" eyebrow="Administration / Activity oversight" description="Review synthetic registration activity summaries without invasive surveillance." icon={UsersRound} kind="officer review" /> : active === 'Audit Logs' ? <GenericModule title="Audit logs" eyebrow="Governance / Accountability" description="Chronological record of administrative actions across the platform." icon={FileClock} kind="audit event" /> : active === 'Reports & Analytics' ? <GenericModule title="Reports & analytics" eyebrow="Insights / Reporting" description="Create structured summaries of verification, anomalies and investigations." icon={FileBarChart} kind="report" /> : active === 'Synchronisation' ? <GenericModule title="Synchronisation" eyebrow="Infrastructure / Offline-first readiness" description="Review connection status and pending data movement in this frontend demonstration." icon={Network} kind="sync event" /> : <GenericModule title="Settings" eyebrow="Administration / Configuration" description="Manage demonstration roles, notifications and system configuration." icon={Settings} kind="setting" />
  const visibleNav = navItems.filter((item) => item.label.toLowerCase().includes(search.toLowerCase()) || !search)
  return <div className="app-shell"><aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}><div className="brand"><span className="brand-mark"><ShieldCheck /></span><div className="brand-name"><strong>VoterGuard</strong><span>Integrity command centre</span></div><button className="mobile-close" onClick={() => setMobileOpen(false)}><X /></button></div><div className="side-section-label">Workspace</div><nav>{visibleNav.map(({ label, icon: Icon, count }) => <button key={label} className={active === label ? 'nav-item active' : 'nav-item'} onClick={() => { setActive(label); setMobileOpen(false) }} title={collapsed ? label : undefined}><Icon /><span>{label}</span>{count && <b>{count}</b>}</button>)}</nav><div className="sidebar-bottom"><div className="integrity-card"><span><LockKeyhole /> Secure workspace</span><small>Prototype · no live data</small><div className="integrity-bar"><i /></div></div><button className="nav-item"><CircleHelp /><span>Help & guidance</span></button><button className="user-block"><span className="avatar">IO</span><span className="user-copy"><strong>Izzy Okafor</strong><small>System administrator</small></span><MoreHorizontal /></button></div></aside><main className="main-area"><header className="topbar"><div className="topbar-left"><button className="menu-button" onClick={() => setMobileOpen(true)}><Menu /></button><button className="collapse-button" onClick={() => setCollapsed(!collapsed)}>{collapsed ? <ChevronRight /> : <ChevronLeft />}</button><div className="breadcrumb"><span>VoterGuard</span><ChevronRight /><strong>{active}</strong></div></div><div className="topbar-actions"><div className="global-search"><Search /><input placeholder="Search records, cases..." value={search} onChange={(e) => setSearch(e.target.value)} /><kbd>⌘ K</kbd></div><div className="system-status"><i /><span>Systems operational</span></div><button className="top-icon"><Bell /><i /></button><span className="top-avatar">IO</span></div></header><div className="content-area">{page}</div><footer className="app-footer"><span><ShieldCheck /> VoterGuard · Protecting the Integrity of Every Vote.</span><span>Developed by <strong>Izzycreativehub</strong> · v0.1 prototype</span></footer></main>{recordOpen && <div className="modal-backdrop" role="presentation" onClick={() => setRecordOpen(null)}><div className="modal-card" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}><div className="modal-header"><div><div className="eyebrow">Flagged record</div><h2>{recordOpen}</h2></div><button className="icon-button" onClick={() => setRecordOpen(null)}><X /></button></div><div className="modal-body"><div className="evidence-banner"><AlertTriangle /><div><strong>Human review required</strong><span>Image integrity indicators detected in synthetic demonstration data.</span></div></div><div className="evidence-grid"><div><span>Registration area</span><strong>Lagos Mainland · Ward 04</strong></div><div><span>Photograph status</span><strong>Requires further examination</strong></div><div><span>Completeness</span><strong>8 of 9 fields present</strong></div><div><span>Assigned reviewer</span><strong>Unassigned</strong></div></div></div><div className="modal-footer"><button className="secondary-button" onClick={() => setRecordOpen(null)}>Close</button><button className="primary-button" onClick={() => setRecordOpen(null)}><FolderSearch /> Open investigation</button></div></div></div>}</div>
}
