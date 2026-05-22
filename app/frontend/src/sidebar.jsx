// Global left-hand navigation sidebar

const NAV = [
  { group: 'Operations', items: [
    { id: 'dashboard',    label: 'Mission Control',       icon: 'LayoutDashboard',  badge: 'PRP' },
    { id: 'harness',      label: 'Agent Harness',         icon: 'ShieldHalf',       badge: 3, badgeTone: 'amber' },
    { id: 'fleet',        label: 'Agent Fleet',           icon: 'BotMessageSquare', badge: '24/40' },
    { id: 'incidents',    label: 'Incidents',             icon: 'Siren',            badge: 1, badgeTone: 'crimson' },
  ]},
  { group: 'Insight', items: [
    { id: 'debt',         label: 'Debt Analytics',        icon: 'BrainCircuit' },
    { id: 'reviews',      label: 'Comprehension Reviews', icon: 'BookCheck' },
    { id: 'lineage',      label: 'Code Lineage',          icon: 'GitBranch' },
    { id: 'tco',          label: 'System TCO',            icon: 'Calculator' },
  ]},
  { group: 'Configuration', items: [
    { id: 'rules',        label: 'Agent.md Ruleset',      icon: 'FileCog' },
    { id: 'sandboxes',    label: 'Sandbox Envelopes',     icon: 'Container' },
    { id: 'integrations', label: 'Integrations',          icon: 'Cable' },
    { id: 'settings',     label: 'Settings',              icon: 'Settings2' },
  ]},
];

function Sidebar({ active, onSelect }) {
  return (
    <aside className="w-[232px] shrink-0 h-full flex flex-col border-r border-ink-700/70 bg-ink-950/80">
      {/* Brand */}
      <div className="h-14 px-4 flex items-center gap-2.5 border-b border-ink-700/70">
        <div className="relative w-7 h-7">
          <div className="absolute inset-0 rounded-sm bg-gradient-to-br from-emerald2-400 to-azure2-500 opacity-90" />
          <div className="absolute inset-[3px] rounded-[2px] bg-ink-950 flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-emerald2-400 pulse-dot" />
          </div>
        </div>
        <div className="leading-tight">
          <div className="text-[13px] font-semibold tracking-tight text-slate-100">HybridEngine</div>
          <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-slate2-500">v2.41 · prod</div>
        </div>
      </div>

      {/* Environment switcher */}
      <button className="mx-3 mt-3 mb-2 h-8 px-2.5 flex items-center justify-between rounded-sm border border-ink-700 hover:border-ink-600 bg-ink-850 text-left">
        <span className="flex items-center gap-2 text-[12px]">
          <Icon name="Globe" className="w-3.5 h-3.5 text-emerald2-400" />
          <span className="text-slate-200">acme-payments</span>
          <span className="font-mono text-[10px] text-slate2-500">prod-us-east-2</span>
        </span>
        <Icon name="ChevronsUpDown" className="w-3 h-3 text-slate2-500" />
      </button>

      {/* Nav groups */}
      <nav className="flex-1 overflow-y-auto px-2 pb-3">
        {NAV.map((g) => (
          <div key={g.group} className="mt-3">
            <div className="px-2 mb-1 font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">
              {g.group}
            </div>
            <ul className="space-y-0.5">
              {g.items.map((it) => {
                const isActive = active === it.id;
                return (
                  <li key={it.id}>
                    <button
                      onClick={() => onSelect(it.id)}
                      className={`group w-full flex items-center gap-2.5 px-2 h-8 rounded-sm text-[12.5px] transition-colors ${
                        isActive
                          ? 'bg-ink-800 text-slate-100 ring-1 ring-inset ring-ink-600'
                          : 'text-slate2-300 hover:bg-ink-850 hover:text-slate-100'
                      }`}
                    >
                      <Icon
                        name={it.icon}
                        className={`w-4 h-4 ${isActive ? 'text-emerald2-400' : 'text-slate2-400 group-hover:text-slate2-300'}`}
                      />
                      <span className="flex-1 text-left truncate">{it.label}</span>
                      {it.badge !== undefined && (
                        <Pill tone={it.badgeTone || 'slate'} className="!px-1 !py-0">{it.badge}</Pill>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* System status footer */}
      <div className="border-t border-ink-700/70 p-3 space-y-2 text-[11px]">
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">Harness</span>
          <span className="inline-flex items-center gap-1.5 text-emerald2-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald2-400 pulse-dot" />
            <span className="font-mono">ARMED</span>
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">Intercept lag</span>
          <span className="font-mono text-slate-200">12ms</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">Quorum</span>
          <span className="font-mono text-slate-200">2 of 3 on-call</span>
        </div>
        <div className="pt-2 mt-2 border-t border-ink-700/70 flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-amber2-500 to-crimson2-500 flex items-center justify-center text-[11px] font-semibold text-ink-950">
            MK
          </div>
          <div className="leading-tight">
            <div className="text-[11.5px] text-slate-100">M. Khoury</div>
            <div className="font-mono text-[10px] text-slate2-500">on-call · primary</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

window.Sidebar = Sidebar;
