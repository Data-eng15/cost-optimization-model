// HybridEngine — Agent Orchestration & Observability
// Root component: composes sidebar, top bar, and four dashboard sections.

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function App() {
  const [active, setActive] = React.useState('dashboard');
  const [tick,   setTick]   = React.useState(0);

  // PRP metrics — slow-drift simulation
  const [velocity,    setVelocity]    = React.useState(224);
  const [throughput,  setThroughput]  = React.useState(43.4);
  const [stability,   setStability]   = React.useState(16.4);
  const [spend,       setSpend]       = React.useState(1042);

  React.useEffect(() => {
    const id = setInterval(() => {
      setTick((t) => t + 1);
      setVelocity((v)   => clamp(v   + (Math.random() - 0.4) * 0.6,  210, 240));
      setThroughput((v) => clamp(v   + (Math.random() - 0.6) * 0.05, 42,  46));
      setStability((v)  => clamp(v   + (Math.random() - 0.4) * 0.06, 15.6, 17.2));
      setSpend((v)      => clamp(v   + (Math.random() - 0.45) * 4,   980, 1120));
    }, 1500);
    return () => clearInterval(id);
  }, []);

  const time = new Date(Date.UTC(2026, 4, 22, 14, 32, 8) + tick * 1500)
    .toISOString().slice(11, 19) + ' UTC';

  return (
    <div className="h-screen w-screen flex bg-ink-900 bg-grid overflow-auto min-w-[1480px]">
      <Sidebar active={active} onSelect={setActive} />

      <main className="flex-1 min-w-0 flex flex-col">
        <TopBar time={time} active={active} />

        <div className="flex-1 overflow-y-auto px-5 py-4">
          {/* Section 1 — PRP Header KPIs */}
          <PRPHeader
            velocity={velocity}
            throughput={throughput}
            stability={stability}
            spend={spend}
          />

          {/* Section 2 — Agent Harness Intercept Pipeline */}
          <div className="grid grid-cols-12 gap-3 mt-4">
            <HarnessPipeline />
          </div>

          {/* Sections 3 & 4 — Comprehension Debt + TCO Calculator */}
          <div className="grid grid-cols-12 gap-3 mt-4 mb-6">
            <ComprehensionDebt />
            <TCOCalculator live={tick} />
          </div>
        </div>
      </main>
    </div>
  );
}

function TopBar({ time, active }) {
  const crumbs = {
    dashboard:    ['Operations', 'Mission Control'],
    harness:      ['Operations', 'Agent Harness'],
    fleet:        ['Operations', 'Agent Fleet'],
    incidents:    ['Operations', 'Incidents'],
    debt:         ['Insight',    'Debt Analytics'],
    reviews:      ['Insight',    'Comprehension Reviews'],
    lineage:      ['Insight',    'Code Lineage'],
    tco:          ['Insight',    'System TCO'],
    rules:        ['Configuration', 'Agent.md Ruleset'],
    sandboxes:    ['Configuration', 'Sandbox Envelopes'],
    integrations: ['Configuration', 'Integrations'],
    settings:     ['Configuration', 'Settings'],
  }[active] || ['Operations', 'Mission Control'];

  return (
    <header className="h-14 shrink-0 border-b border-ink-700/70 bg-ink-950/60 backdrop-blur flex items-center px-5 gap-4 whitespace-nowrap">
      {/* Breadcrumbs */}
      <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate2-400 shrink-0">
        <span>{crumbs[0]}</span>
        <Icon name="ChevronRight" className="w-3 h-3 text-slate2-600" />
        <span className="text-slate-100">{crumbs[1]}</span>
        <Pill tone="emerald" dot className="ml-2">LIVE</Pill>
      </div>

      {/* Command search */}
      <div className="flex-1 max-w-md">
        <button className="w-full h-8 px-2.5 flex items-center gap-2.5 rounded-sm border border-ink-700 hover:border-ink-600 bg-ink-850/60 text-left">
          <Icon name="Search" className="w-3.5 h-3.5 text-slate2-500 shrink-0" />
          <span className="text-[11.5px] text-slate2-400 flex-1 truncate">
            Run command, route to agent, query log…
          </span>
          <Kbd>⌘</Kbd><Kbd>K</Kbd>
        </button>
      </div>

      {/* Right cluster */}
      <div className="flex items-center gap-2 shrink-0">
        <div className="hidden xl:flex items-center gap-3 pr-3 border-r border-ink-700/70">
          <TopStat label="incidents"   value="1"     tone="crimson" />
          <TopStat label="intercepts/h" value="38"   tone="amber"  />
          <TopStat label="agents"      value="24/40" tone="emerald" />
        </div>
        <Btn size="sm" variant="ghost" icon="Bell">3</Btn>
        <Btn size="sm" variant="ghost" icon="GitPullRequest">PRs</Btn>
        <Btn size="sm" variant="amber" icon="ShieldAlert">1 awaiting HITL</Btn>
        <div className="pl-2 ml-1 border-l border-ink-700/70 font-mono text-[10.5px] text-slate2-400 tabular-nums">
          {time}
        </div>
      </div>
    </header>
  );
}

function TopStat({ label, value, tone }) {
  const tones = {
    crimson: 'text-crimson2-400',
    amber:   'text-amber2-400',
    emerald: 'text-emerald2-400',
  };
  return (
    <div className="flex items-baseline gap-1.5 font-mono text-[10.5px]">
      <span className="uppercase tracking-[0.14em] text-slate2-500">{label}</span>
      <span className={`tabular-nums ${tones[tone]}`}>{value}</span>
    </div>
  );
}

// Boot
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
