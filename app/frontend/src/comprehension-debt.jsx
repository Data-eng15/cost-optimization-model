// Section 3 — Comprehension Debt Analytics
// Cognitive decay tracker, sprint estimation rule slider, comprehension review checklist.

const MODULES = [
  { name: 'payments/checkout-orchestrator.ts', author: 'agt-7c41 → S. Volkova', loc: 1842, comp: 42, churn: 'high',   ttl: '2d',      tier: 'tier-0' },
  { name: 'ledger/reconciliation.rs',          author: 'agt-2bd1 → R. Okafor',  loc: 964,  comp: 58, churn: 'medium', ttl: '5d',      tier: 'tier-1' },
  { name: 'auth/session-token-rotator.go',     author: 'agt-9f02 → M. Khoury',  loc: 432,  comp: 71, churn: 'low',    ttl: '11d',     tier: 'tier-0' },
  { name: 'gql/resolvers/inventory.ts',        author: 'agt-4e88 → J. Pham',    loc: 2104, comp: 31, churn: 'high',   ttl: 'overdue', tier: 'tier-1' },
  { name: 'workers/email-digest.py',           author: 'agt-2bd1 → R. Okafor',  loc: 287,  comp: 88, churn: 'low',    ttl: '14d',     tier: 'tier-2' },
];

const REVIEWS = [
  { who: 'S. Volkova', mod: 'checkout-orchestrator.ts',  state: 'overdue', due: '−1d' },
  { who: 'J. Pham',    mod: 'resolvers/inventory.ts',    state: 'overdue', due: '−3h' },
  { who: 'R. Okafor',  mod: 'reconciliation.rs',         state: 'pending', due: '2d'  },
  { who: 'M. Khoury',  mod: 'session-token-rotator.go',  state: 'done',    due: '✓'   },
  { who: 'A. Iyer',    mod: 'workers/email-digest.py',   state: 'done',    due: '✓'   },
];

function ComprehensionDebt() {
  const [audit, setAudit] = React.useState(40);

  React.useEffect(() => {
    const el = document.querySelector('.cd-slider');
    if (el) el.style.setProperty('--p', `${audit}%`);
  }, [audit]);

  const sprintHrs = 80;
  const auditHrs  = Math.round((audit / 100) * sprintHrs);
  const buildHrs  = sprintHrs - auditHrs;

  return (
    <Panel
      eyebrow="LONG-TERM HEALTH"
      title="Comprehension Debt Analytics"
      className="col-span-8"
      actions={
        <>
          <Pill tone="crimson" dot>11 modules &lt; 60%</Pill>
          <Btn size="xs" icon="FileText">Export report</Btn>
        </>
      }
    >
      <div className="grid grid-cols-12 gap-3">
        {/* Cognitive Decay Tracker */}
        <div className="col-span-7">
          <div className="flex items-center justify-between mb-2">
            <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">
              Cognitive Decay · Recently merged AI modules
            </div>
            <div className="flex items-center gap-2 font-mono text-[10px] text-slate2-500">
              <span className="inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald2-400" /> ≥ 75%</span>
              <span className="inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-amber2-400"   /> 60–74%</span>
              <span className="inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-crimson2-400" /> &lt; 60%</span>
            </div>
          </div>

          <div className="rounded-md border border-ink-700/70 overflow-hidden">
            <div className="grid grid-cols-[1.6fr_0.9fr_0.5fr_0.85fr] gap-3 px-3 py-1.5 border-b border-ink-700/60 bg-ink-900/60 font-mono text-[10px] uppercase tracking-[0.14em] text-slate2-500">
              <span>Module · authoring chain</span>
              <span>Comprehension</span>
              <span className="text-right">LOC AI</span>
              <span className="text-right">Review TTL</span>
            </div>
            <ul>
              {MODULES.map((m) => {
                const tone     = m.comp >= 75 ? 'emerald' : m.comp >= 60 ? 'amber' : 'crimson';
                const barColor = tone === 'emerald' ? '#10D58A' : tone === 'amber' ? '#FFB020' : '#FF2A4D';
                return (
                  <li key={m.name} className="grid grid-cols-[1.6fr_0.9fr_0.5fr_0.85fr] gap-3 px-3 py-2.5 border-b border-ink-700/40 last:border-b-0 hover:bg-ink-850/60">
                    <div className="min-w-0">
                      <div className="font-mono text-[11.5px] text-slate-100 truncate">{m.name}</div>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <Pill
                          tone={m.tier === 'tier-0' ? 'crimson' : m.tier === 'tier-1' ? 'amber' : 'slate'}
                          className="!py-0"
                        >
                          {m.tier}
                        </Pill>
                        <span className="font-mono text-[10px] text-slate2-500 truncate">{m.author}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 rounded-full bar-track overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${m.comp}%`, background: barColor, boxShadow: `0 0 8px ${barColor}55` }}
                        />
                      </div>
                      <span className={`font-mono text-[11px] tabular-nums ${
                        tone === 'emerald' ? 'text-emerald2-400' : tone === 'amber' ? 'text-amber2-400' : 'text-crimson2-400'
                      }`}>
                        {m.comp}%
                      </span>
                    </div>
                    <div className="text-right font-mono text-[11px] text-slate-200 tabular-nums">{m.loc.toLocaleString()}</div>
                    <div className="text-right font-mono text-[11px]">
                      <span className={m.ttl === 'overdue' ? 'text-crimson2-400' : 'text-slate-200'}>{m.ttl}</span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Sprint Estimation Rule Calculator */}
          <div className="mt-3 rounded-md border border-ink-700/70 bg-ink-900/40 p-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="text-[12px] font-semibold text-slate-100">Sprint Estimation Rule</div>
                <div className="font-mono text-[10px] text-slate2-500">Enforced ≥ 30% audit buffer — hard-cap at PR merge time</div>
              </div>
              <Pill tone={audit >= 40 ? 'emerald' : audit >= 30 ? 'amber' : 'crimson'} dot>
                BUFFER {audit}%
              </Pill>
            </div>

            <div className="flex items-center gap-3 mb-3">
              <input
                type="range" min="0" max="80" step="5"
                value={audit}
                onChange={(e) => setAudit(+e.target.value)}
                className="slider cd-slider"
              />
              <span className="font-mono text-[11px] text-amber2-400 w-10 text-right tabular-nums">{audit}%</span>
            </div>

            {/* Allocation bar */}
            <div className="h-7 w-full rounded-sm overflow-hidden flex border border-ink-700/60">
              <div
                className="bg-azure2-500/35 border-r border-ink-900 flex items-center justify-center font-mono text-[10px] text-azure2-400"
                style={{ width: `${100 - audit}%` }}
              >
                BUILD · {buildHrs}h
              </div>
              <div
                className="bg-amber2-500/25 flex items-center justify-center font-mono text-[10px] text-amber2-400"
                style={{ width: `${audit}%` }}
              >
                AUDIT · {auditHrs}h
              </div>
            </div>

            <div className="mt-2 flex items-center justify-between font-mono text-[10px] text-slate2-500">
              <span>2-week sprint · capacity {sprintHrs}h/eng</span>
              <span>
                {audit < 30
                  ? <span className="text-crimson2-400">⚠ below minimum — sprint will fail policy R-031</span>
                  : <span className="text-emerald2-400">✓ policy R-031 satisfied</span>
                }
              </span>
            </div>
          </div>
        </div>

        {/* Mandatory Comprehension Reviews */}
        <div className="col-span-5">
          <div className="rounded-md border border-ink-700/70 bg-ink-900/50 h-full flex flex-col">
            <div className="px-3 py-2 border-b border-ink-700/60 flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">
                Mandatory comprehension reviews
              </span>
              <Pill tone="amber">SPRINT-87 · CLOSES 18:00</Pill>
            </div>
            <ul className="divide-y divide-ink-700/40 flex-1">
              {REVIEWS.map((r) => {
                const isOverdue = r.state === 'overdue';
                const isDone    = r.state === 'done';
                return (
                  <li key={r.who} className="px-3 py-2.5 flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-sm border flex items-center justify-center shrink-0 ${
                      isDone
                        ? 'border-emerald2-500/60 bg-emerald2-500/15'
                        : isOverdue
                          ? 'border-crimson2-500/60 bg-crimson2-500/10 blink-amber'
                          : 'border-ink-600 bg-ink-850'
                    }`}>
                      {isDone    && <Icon name="Check" className="w-3 h-3 text-emerald2-400" />}
                      {isOverdue && <Icon name="Clock" className="w-3 h-3 text-crimson2-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-[12px] text-slate-100">{r.who}</div>
                      <div className="font-mono text-[10.5px] text-slate2-400 truncate">verbal · {r.mod}</div>
                    </div>
                    <div className="text-right">
                      <div className={`font-mono text-[11px] ${
                        isOverdue ? 'text-crimson2-400' : isDone ? 'text-emerald2-400' : 'text-slate-200'
                      }`}>
                        {r.due}
                      </div>
                      <div className="font-mono text-[10px] text-slate2-500 uppercase">{r.state}</div>
                    </div>
                  </li>
                );
              })}
            </ul>
            <div className="px-3 py-2 border-t border-ink-700/60 flex items-center justify-between font-mono text-[10px] text-slate2-500">
              <span>3 / 5 complete</span>
              <Btn size="xs" icon="CalendarClock">Schedule walk-throughs</Btn>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  );
}

window.ComprehensionDebt = ComprehensionDebt;
