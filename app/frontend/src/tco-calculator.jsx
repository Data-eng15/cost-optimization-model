// Section 4 — Economic TCO Calculator
// Side-by-side: Human Capital loaded cost vs. Agent Compute burn rate with live ticker.

function TCOCalculator({ live }) {
  // Human side — interactive inputs
  const [salary,  setSalary]  = React.useState(165000);
  const [loading, setLoading] = React.useState(1.32);  // benefits + overhead multiplier
  const [recruit, setRecruit] = React.useState(28000);
  const [rampWk,  setRampWk]  = React.useState(12);

  const humanLoaded = Math.round(salary * loading + recruit + (salary / 52) * rampWk * 0.5);

  // Agent side — animated burn rate
  const agentDaily  = Math.round(1000 + Math.sin(live / 4) * 70 + (live % 11) * 6);
  const agentAnnual = Math.round(agentDaily * 365 + 4800 /* licenses */);
  const delta       = agentAnnual - humanLoaded;
  const agentHigher = delta > 0;

  return (
    <Panel
      eyebrow="ECONOMICS · ANNUALIZED"
      title="System TCO · Human Capital vs. Agent Compute"
      className="col-span-4"
      actions={
        <Pill tone={agentHigher ? 'crimson' : 'emerald'} dot>
          {agentHigher ? 'AGENT > HUMAN' : 'AGENT < HUMAN'}
        </Pill>
      }
    >
      <div className="grid grid-cols-2 gap-2">
        {/* Human column */}
        <div className="rounded-md border border-ink-700/70 bg-ink-900/40 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Icon name="Users" className="w-3.5 h-3.5 text-azure2-400" />
            <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-azure2-400">Human capital</span>
          </div>

          <Field label="Base salary"     value={salary}  onChange={setSalary}  prefix="$" max={400000} step={5000} />
          <Field label="Loading factor"  value={loading} onChange={setLoading} suffix="×" step={0.01} min={1} max={2} fixed={2} />
          <Field label="Recruitment"     value={recruit} onChange={setRecruit} prefix="$" max={150000} step={1000} />
          <Field label="Ramp-up (weeks)" value={rampWk}  onChange={setRampWk} suffix="w" max={52} step={1} />

          <div className="mt-2 pt-2 border-t border-ink-700/60">
            <div className="font-mono text-[10px] text-slate2-500 uppercase tracking-[0.18em]">Annual loaded</div>
            <div className="font-mono text-[22px] text-slate-100 leading-none mt-1 tabular-nums">
              ${humanLoaded.toLocaleString()}
            </div>
            <div className="font-mono text-[10px] text-slate2-500 mt-1">deterministic · 1 FTE</div>
          </div>
        </div>

        {/* Agent column */}
        <div className={`relative rounded-md border bg-ink-900/40 p-3 overflow-hidden ${
          agentHigher ? 'border-crimson2-500/40' : 'border-ink-700/70'
        }`}>
          {/* Live progress strip */}
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-amber2-500/40">
            <div className="h-full bg-amber2-400" style={{ width: `${(live % 60) / 60 * 100}%` }} />
          </div>

          <div className="flex items-center gap-2 mb-2">
            <Icon name="Bot" className="w-3.5 h-3.5 text-amber2-400" />
            <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-amber2-400">Agent compute</span>
          </div>

          <Row label="License (annual)" value="$4,800" />
          <Row label="Context window"   value="142,000 tok" />
          <Row label="Tokens / loop"    value="~ 28k in · 6k out" />
          <Row label="Active loops"     value={`${24 + (live % 7)} concurrent`} />

          <div className="mt-2 pt-2 border-t border-ink-700/60">
            <div className="font-mono text-[10px] text-amber2-400 uppercase tracking-[0.18em] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber2-400 pulse-dot" />
              Live burn · 24h rolling
            </div>
            <div className="font-mono text-[22px] text-amber2-400 leading-none mt-1 tabular-nums">
              ${agentDaily.toLocaleString()}<span className="text-[12px] text-slate2-400"> /day</span>
            </div>

            <div className="mt-2 font-mono text-[10px] text-slate2-500 uppercase tracking-[0.18em]">Annualized</div>
            <div className={`font-mono text-[18px] leading-none mt-1 tabular-nums ${
              agentHigher ? 'text-crimson2-400' : 'text-emerald2-400'
            }`}>
              ${agentAnnual.toLocaleString()}
            </div>
            <div className="font-mono text-[10px] text-slate2-500 mt-1">unsupervised loop assumption</div>
          </div>
        </div>
      </div>

      {/* Delta strip */}
      <div className={`mt-3 rounded-md border px-3 py-2 flex items-center gap-3 ${
        agentHigher
          ? 'border-crimson2-500/40 bg-crimson2-500/[0.06]'
          : 'border-emerald2-500/40 bg-emerald2-500/[0.05]'
      }`}>
        <Icon
          name={agentHigher ? 'TrendingUp' : 'TrendingDown'}
          className={`w-4 h-4 ${agentHigher ? 'text-crimson2-400' : 'text-emerald2-400'}`}
        />
        <div className="flex-1 min-w-0">
          <div className="text-[12px] text-slate-100">
            {agentHigher
              ? 'Agent loops cost more than the equivalent FTE'
              : 'Agent envelope still under FTE cost'}
          </div>
          <div className="font-mono text-[10px] text-slate2-500">
            Δ {agentHigher ? '+' : '−'}${Math.abs(delta).toLocaleString()}/yr · break-even at ~${Math.round(humanLoaded / 365).toLocaleString()}/day
          </div>
        </div>
        <Btn size="xs" icon="Wand2">Optimize loop</Btn>
      </div>

      {/* Live ticker tape */}
      <div className="mt-2 overflow-hidden rounded-sm border border-ink-700/60 bg-ink-950/80">
        <div className="marquee-track whitespace-nowrap font-mono text-[10.5px] text-slate2-400 py-1.5">
          {Array.from({ length: 2 }).map((_, k) => (
            <span key={k}>
              <T label="tok-in"   v={`${(2810 + (live % 99)).toLocaleString()}/s`} />
              <T label="tok-out"  v={`${(640  + (live % 31)).toLocaleString()}/s`} />
              <T label="$/min"    v={`$${(0.71 + (live % 13) / 100).toFixed(2)}`} tone="amber" />
              <T label="ctx-fill" v={`${82 + (live % 18)}%`} />
              <T label="loop-id"  v={`loop_${(48201 + live).toString(16)}`} />
              <T label="cache-hit"v={`${44 + (live % 17)}%`} />
              <T label="retries"  v={`${live % 4}`} />
            </span>
          ))}
        </div>
      </div>
    </Panel>
  );
}

function Field({ label, value, onChange, prefix, suffix, step = 1, min = 0, max = 1000000, fixed = 0 }) {
  return (
    <label className="flex items-center justify-between gap-2 py-1">
      <span className="text-[11px] text-slate2-400">{label}</span>
      <div className="inline-flex items-center gap-1 font-mono text-[11px]">
        {prefix && <span className="text-slate2-500">{prefix}</span>}
        <input
          type="number"
          value={fixed ? (+value).toFixed(fixed) : value}
          min={min} max={max} step={step}
          onChange={(e) => onChange(+e.target.value)}
          className="w-20 bg-ink-850 border border-ink-700 rounded-sm px-1.5 py-0.5 text-right text-slate-100 focus:outline-none focus:border-azure2-500"
        />
        {suffix && <span className="text-slate2-500">{suffix}</span>}
      </div>
    </label>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between py-1 font-mono text-[11px]">
      <span className="text-slate2-400">{label}</span>
      <span className="text-slate-100 tabular-nums">{value}</span>
    </div>
  );
}

function T({ label, v, tone }) {
  return (
    <span className="mx-3 inline-flex items-center gap-1">
      <span className="text-slate2-500 uppercase tracking-[0.12em] text-[9.5px]">{label}</span>
      <span className={tone === 'amber' ? 'text-amber2-400' : 'text-slate-200'}>{v}</span>
      <span className="text-slate2-700">·</span>
    </span>
  );
}

window.TCOCalculator = TCOCalculator;
