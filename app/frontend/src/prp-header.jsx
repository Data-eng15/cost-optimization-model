// Section 1 — Top-Level Metrics Header (PRP Dashboard)
// Exposes the Productivity-Reliability Paradox across 4 KPI cards.

function PRPHeader({ velocity, throughput, stability, spend }) {
  const cards = [
    {
      eyebrow: 'INDIVIDUAL · AUTHOR',
      label:   'Token Velocity / Author',
      value:   velocity.toFixed(0),
      unit:    'k tok/day',
      delta:   '+45.2%',
      sub:     'MoM · cohort: 142 engineers',
      tone:    'amber',
      icon:    'Zap',
      trail:   'Individual output diverging from system output — classic PRP signal.',
      data:    [62, 68, 73, 80, 86, 95, 110, 132, 150, 168, 184, 198, 212, 224],
    },
    {
      eyebrow: 'SYSTEM · MERGED',
      label:   'Codebase Throughput',
      value:   throughput.toFixed(1),
      unit:    'PR/day',
      delta:   '-1.5%',
      sub:     'merge-rate · 28d trailing',
      tone:    'slate',
      icon:    'GitMerge',
      trail:   'Net merged work is flat-to-down despite individual velocity surging.',
      data:    [44, 46, 45, 47, 46, 45, 44, 45, 46, 45, 44, 44, 43, 43],
    },
    {
      eyebrow: 'RELIABILITY · CHANGE-FAIL',
      label:   'Delivery Stability',
      value:   stability.toFixed(1),
      unit:    '% CFR',
      delta:   '-7.2%',
      sub:     'change-failure rate · rising',
      tone:    'crimson',
      icon:    'AlertTriangle',
      trail:   'Stability eroding — incidents-per-deploy up across 4 of 6 services.',
      data:    [9.0, 9.4, 10.1, 10.8, 11.6, 12.2, 12.5, 13.1, 13.4, 14.0, 14.6, 15.2, 15.8, 16.4],
      isBad:   true,
    },
    {
      eyebrow: 'ECONOMIC · BURN',
      label:   'Agent Compute Spend',
      value:   '$' + spend.toLocaleString(),
      unit:    '/day',
      delta:   '2.1× human budget',
      sub:     'rolling 24h · tokens billed',
      tone:    'amber',
      icon:    'Flame',
      trail:   'Unsupervised loops on >100k-tok contexts inflate run-rate weekly.',
      data:    [310, 340, 380, 420, 470, 540, 610, 700, 790, 880, 940, 990, 1020, 1075],
    },
  ];

  return (
    <div>
      {/* Paradox banner */}
      <div className="mb-3 flex items-center gap-3 px-3 py-2 rounded-md border border-amber2-500/30 bg-amber2-500/[0.05] tape">
        <Icon name="ActivitySquare" className="w-4 h-4 text-amber2-400" />
        <div className="text-[12px] text-slate-100">
          <span className="font-semibold">Productivity-Reliability Paradox detected.</span>
          <span className="text-slate2-300"> Author velocity is up 45% MoM while system stability has dropped 7.2%. Authoring comprehension trending below 60% across 11 modules.</span>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <Pill tone="amber" dot>PARADOX · ACTIVE</Pill>
          <Btn variant="ghost" size="xs" icon="ExternalLink">Open analysis</Btn>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {cards.map((c) => <KPICard key={c.label} card={c} />)}
      </div>
    </div>
  );
}

function KPICard({ card }) {
  const tones = {
    amber:   { color: '#FFB020', ring: 'ring-amber2-500/40',   text: 'text-amber2-400' },
    crimson: { color: '#FF2A4D', ring: 'ring-crimson2-500/40', text: 'text-crimson2-400' },
    emerald: { color: '#10D58A', ring: 'ring-emerald2-500/40', text: 'text-emerald2-400' },
    slate:   { color: '#7C88A8', ring: 'ring-ink-600',         text: 'text-slate2-300' },
  };
  const t = tones[card.tone];

  const deltaIcon = card.delta.startsWith('-')
    ? 'TrendingDown'
    : card.delta.startsWith('+')
      ? 'TrendingUp'
      : 'ArrowUpRight';

  return (
    <div className={`relative rounded-md border border-ink-700/80 bg-ink-850/70 p-3.5 overflow-hidden ${
      card.tone === 'amber' || card.tone === 'crimson' ? 'ring-1 ' + t.ring : ''
    }`}>
      {/* Eyebrow */}
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">{card.eyebrow}</span>
        <Icon name={card.icon} className={`w-3.5 h-3.5 ${t.text}`} />
      </div>

      {/* Label */}
      <div className="text-[12px] text-slate2-400 mb-1.5">{card.label}</div>

      {/* Value */}
      <div className="flex items-baseline gap-1.5">
        <span className="font-mono text-[28px] leading-none font-semibold text-slate-100 tabular-nums">{card.value}</span>
        <span className="font-mono text-[11px] text-slate2-400">{card.unit}</span>
      </div>

      {/* Delta + sub */}
      <div className="mt-2.5 flex items-center justify-between">
        <span className={`inline-flex items-center gap-1 font-mono text-[11px] ${t.text}`}>
          <Icon name={deltaIcon} className="w-3 h-3" />
          {card.delta}
        </span>
        <span className="font-mono text-[10px] text-slate2-500">{card.sub}</span>
      </div>

      {/* Sparkline */}
      <div className="mt-3 -mx-1.5">
        <Sparkline data={card.data} color={t.color} width={220} height={36} />
      </div>

      {/* Trail */}
      <div className="mt-2 pt-2 border-t border-ink-700/60 text-[10.5px] leading-snug text-slate2-400">
        {card.trail}
      </div>
    </div>
  );
}

window.PRPHeader = PRPHeader;
