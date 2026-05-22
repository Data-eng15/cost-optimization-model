// Section 2 — Live Agent Harness Intercept Pipeline (centerpiece)
// Three-stage sandboxed execution envelope: tty capture → Agent.md rule eval → HITL approval.

const AGENT_FEED = [
  { id: 'agt-7c41', name: 'agt://refactor-billing-svc',  status: 'EXECUTING', model: 'claude-sonnet-4.6', ttl: '00:08:42' },
  { id: 'agt-9f02', name: 'agt://infra-migrate-staging', status: 'HARNESS',   model: 'gpt-5.1-turbo',    ttl: '00:03:11' },
  { id: 'agt-2bd1', name: 'agt://chore-deps-bump',       status: 'EXECUTING', model: 'claude-haiku-4.5', ttl: '00:14:55' },
  { id: 'agt-4e88', name: 'agt://gen-graphql-resolvers', status: 'IDLE',      model: 'gpt-5.1-turbo',    ttl: '—' },
];

const STAGE1_LINES = [
  { t: '14:32:08.114', tag: 'shell',   text: '$ railway run --service api-prod --env production' },
  { t: '14:32:08.231', tag: 'shell',   text: '$ railway volume list --service postgres-primary' },
  { t: '14:32:08.402', tag: 'graphql', text: 'mutation { volumeDelete(volumeId: "vol_8af2…", force: true) }' },
  { t: '14:32:08.517', tag: 'shell',   text: '$ git push origin main --force-with-lease' },
];

function HarnessPipeline() {
  const [resolved,   setResolved]   = React.useState(null); // 'approved' | 'blocked' | null
  const [armConfirm, setArmConfirm] = React.useState(false);
  const [selected,   setSelected]   = React.useState('agt-9f02');

  function handleApprove() { if (armConfirm) setResolved('approved'); }
  function handleBlock()   { setResolved('blocked'); }
  function handleReset()   { setResolved(null); setArmConfirm(false); }

  return (
    <Panel
      eyebrow="LIVE · 4 AGENTS"
      title="Agent Harness Intercept Pipeline"
      className="col-span-12"
      actions={
        <>
          <Pill tone="emerald" dot>HARNESS ARMED</Pill>
          <Pill tone="slate"><Icon name="Cpu" className="w-3 h-3 mr-1" />local-proxy · 12ms</Pill>
          <Btn size="xs" icon="ListFilter">Filter</Btn>
          <Btn size="xs" icon="Pause">Pause feed</Btn>
        </>
      }
    >
      <div className="grid grid-cols-12 gap-3">
        {/* Active agent list (left rail) */}
        <div className="col-span-3">
          <div className="rounded-md border border-ink-700/70 bg-ink-900/60 overflow-hidden">
            <div className="px-3 py-2 border-b border-ink-700/60 flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">Active sessions</span>
              <span className="font-mono text-[10px] text-slate2-500">4 / 40</span>
            </div>
            <ul>
              {AGENT_FEED.map((a) => {
                const isSel = selected === a.id;
                const tone  = a.status === 'HARNESS' ? 'amber' : a.status === 'EXECUTING' ? 'emerald' : 'slate';
                return (
                  <li key={a.id}>
                    <button
                      onClick={() => setSelected(a.id)}
                      className={`w-full text-left px-3 py-2 border-b border-ink-700/40 last:border-b-0 transition-colors ${
                        isSel ? 'bg-ink-800/80' : 'hover:bg-ink-850/80'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          a.status === 'HARNESS'   ? 'bg-amber2-400 pulse-dot'
                          : a.status === 'EXECUTING' ? 'bg-emerald2-400 pulse-dot'
                          : 'bg-slate2-500'
                        }`} />
                        <span className="font-mono text-[11px] text-slate-100 truncate">{a.name}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <Pill tone={tone}>{a.status}</Pill>
                        <span className="font-mono text-[10px] text-slate2-500">{a.ttl}</span>
                      </div>
                      <div className="mt-1 font-mono text-[10px] text-slate2-500 truncate">{a.model}</div>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        {/* Pipeline stages */}
        <div className="col-span-9 grid grid-cols-3 gap-3">
          <Stage1 />
          <Stage2 />
          <Stage3
            resolved={resolved}
            armConfirm={armConfirm}
            setArmConfirm={setArmConfirm}
            onApprove={handleApprove}
            onBlock={handleBlock}
            onReset={handleReset}
          />
        </div>
      </div>

      {/* Pipeline footer stats */}
      <div className="mt-3 flex items-center justify-between text-[11px] text-slate2-400">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">Last hour</span>
          <span><span className="text-emerald2-400 font-mono">412</span> approved</span>
          <span><span className="text-amber2-400  font-mono">38</span>  intercepted</span>
          <span><span className="text-crimson2-400 font-mono">6</span>  blocked &amp; rolled back</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Kbd>⌘</Kbd><Kbd>↵</Kbd>
          <span className="text-slate2-500">approve · </span>
          <Kbd>⌘</Kbd><Kbd>⌫</Kbd>
          <span className="text-slate2-500">terminate</span>
        </div>
      </div>
    </Panel>
  );
}

// ──────────────────────── Stage 1 ────────────────────────
function Stage1() {
  return (
    <StageShell idx="01" title="Agent Execution Container" sub="sandboxed envelope · network: egress-deny" tone="azure">
      <div className="relative h-[260px] rounded-sm border border-ink-700/70 bg-ink-950/80 overflow-hidden scanline">
        <div className="px-3 py-1.5 border-b border-ink-700/60 flex items-center justify-between bg-ink-900/80">
          <span className="font-mono text-[10px] text-slate2-400">agt-9f02 · tty0</span>
          <span className="font-mono text-[10px] text-emerald2-400">● capturing</span>
        </div>
        <div className="p-3 font-mono text-[11px] leading-relaxed space-y-1.5">
          {STAGE1_LINES.map((l, i) => (
            <div key={i} className="flex gap-2.5">
              <span className="text-slate2-500 shrink-0">{l.t}</span>
              <span className={l.tag === 'graphql' ? 'text-amber2-400' : 'text-slate-200'}>{l.text}</span>
            </div>
          ))}
          <div className="flex gap-2.5">
            <span className="text-slate2-500 shrink-0">14:32:08.612</span>
            <span className="text-slate-300">$ <span className="inline-block w-1.5 h-3 -mb-0.5 bg-emerald2-400 align-middle pulse-dot" /></span>
          </div>
        </div>
      </div>
      <div className="mt-2 flex items-center justify-between text-[10.5px] font-mono text-slate2-500">
        <span>fs: read-only · /workspace</span>
        <span>cpu 18%  mem 412MB</span>
      </div>
    </StageShell>
  );
}

// ──────────────────────── Stage 2 ────────────────────────
function Stage2() {
  return (
    <StageShell idx="02" title="Agent Harness Filter" sub="local-proxy · Agent.md ruleset v17" tone="amber">
      <div className="rounded-sm border border-ink-700/70 bg-ink-950/80 p-3 h-[260px] flex flex-col">
        {/* Triggered rule */}
        <div className="rounded-sm border border-amber2-500/45 bg-amber2-500/[0.08] p-2.5">
          <div className="flex items-center justify-between mb-1.5">
            <span className="inline-flex items-center gap-1.5 font-mono text-[10px] text-amber2-400">
              <Icon name="AlertTriangle" className="w-3 h-3" />
              RULE TRIGGERED
            </span>
            <span className="font-mono text-[10px] text-slate2-500">rule-id: R-074</span>
          </div>
          <div className="font-mono text-[11px] text-slate-100 leading-snug">
            Broad <span className="text-amber2-400">volumeDelete</span> mutation detected on Railway CLI without explicit volume scope.
          </div>
          <div className="mt-1.5 font-mono text-[10px] text-slate2-400">
            matched: <span className="text-amber2-400">CLASS_DESTRUCTIVE_STORAGE</span> · severity <span className="text-amber2-400">P1</span>
          </div>
        </div>

        {/* Evaluation chain */}
        <div className="mt-2.5 flex-1 overflow-y-auto pr-1">
          <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500 mb-1.5">Evaluation chain</div>
          <ul className="space-y-1 font-mono text-[10.5px]">
            <ChainItem state="pass"    label="ALLOW_READ_FILESYSTEM" />
            <ChainItem state="pass"    label="ALLOW_NETWORK_LOOPBACK" />
            <ChainItem state="pass"    label="DENY_PROD_WRITES_WITHOUT_TICKET" subtle />
            <ChainItem state="pass"    label="DENY_FORCE_PUSH_PROTECTED" subtle />
            <ChainItem state="hold"    label="HITL_REQUIRED_VOLUME_MUTATION" />
            <ChainItem state="pending" label="DENY_RM_RECURSIVE_ROOT" subtle />
            <ChainItem state="pending" label="DENY_SECRET_EXFIL" subtle />
          </ul>
        </div>

        <div className="mt-2 pt-2 border-t border-ink-700/60 flex items-center justify-between font-mono text-[10px] text-slate2-500">
          <span>policies evaluated: 41/41</span>
          <span className="text-amber2-400">→ escalating to HITL</span>
        </div>
      </div>
      <div className="mt-2 flex items-center justify-between text-[10.5px] font-mono text-slate2-500">
        <span>Agent.md sha · 9e3a4f1</span>
        <span>p99 eval · 11ms</span>
      </div>
    </StageShell>
  );
}

function ChainItem({ state, label, subtle = false }) {
  const cfg = {
    pass:    { icon: 'Check', tone: 'text-emerald2-400' },
    hold:    { icon: 'Hand',  tone: 'text-amber2-400'   },
    pending: { icon: 'Minus', tone: 'text-slate2-500'   },
  }[state];
  return (
    <li className={`flex items-center gap-2 ${subtle ? 'opacity-70' : ''}`}>
      <Icon name={cfg.icon} className={`w-3 h-3 ${cfg.tone}`} />
      <span className={state === 'pending' ? 'text-slate2-500' : 'text-slate2-300'}>{label}</span>
    </li>
  );
}

// ──────────────────────── Stage 3 ────────────────────────
function Stage3({ resolved, armConfirm, setArmConfirm, onApprove, onBlock, onReset }) {
  const subText = resolved === null
    ? 'awaiting physical-keyboard approval'
    : resolved === 'approved' ? 'approved & promoted'
    : 'terminated & rolled back';

  const stageTone = resolved === null ? 'amber' : resolved === 'approved' ? 'emerald' : 'crimson';

  return (
    <StageShell idx="03" title="Human Intercept Point" sub={subText} tone={stageTone}>
      <div className={`rounded-sm border h-[260px] flex flex-col ${
        resolved === null
          ? 'border-amber2-500/55 bg-amber2-500/[0.04]'
          : resolved === 'approved'
            ? 'border-emerald2-500/45 bg-emerald2-500/[0.05]'
            : 'border-crimson2-500/55 bg-crimson2-500/[0.05]'
      }`}>
        {/* Blinking banner */}
        {resolved === null && (
          <div className="blink-amber border-b px-2.5 py-1.5 flex items-center gap-2">
            <Icon name="ShieldAlert" className="w-3.5 h-3.5 text-amber2-400" />
            <span className="font-mono text-[10.5px] uppercase tracking-[0.14em] text-amber2-400">
              Critical action blocked · physical keyboard approval required
            </span>
          </div>
        )}

        <div className="p-3 flex-1 overflow-y-auto">
          <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500 mb-1">Pending mutation</div>
          <div className="font-mono text-[12px] text-slate-100 leading-snug break-all">
            <span className="text-amber2-400">volumeDelete</span>(volumeId:{' '}
            <span className="text-azure2-400">"vol_8af2c1…"</span>, force:{' '}
            <span className="text-crimson2-400">true</span>)
          </div>

          <dl className="mt-3 grid grid-cols-2 gap-y-1.5 gap-x-3 font-mono text-[10.5px]">
            <dt className="text-slate2-500">target</dt>
            <dd className="text-slate-200 text-right">postgres-primary · prod</dd>
            <dt className="text-slate2-500">data at risk</dt>
            <dd className="text-crimson2-400 text-right">487 GB · 41M rows</dd>
            <dt className="text-slate2-500">blast radius</dt>
            <dd className="text-crimson2-400 text-right">tier-0 · checkout</dd>
            <dt className="text-slate2-500">rollback</dt>
            <dd className="text-slate-200 text-right">point-in-time · 14:31:01</dd>
            <dt className="text-slate2-500">requesting agent</dt>
            <dd className="text-slate-200 text-right">agt://infra-migrate-staging</dd>
          </dl>

          {/* Arm toggle */}
          {resolved === null && (
            <div className="mt-3 rounded-sm border border-ink-700 bg-ink-900/70 px-2.5 py-2 flex items-center gap-2">
              <Toggle on={armConfirm} onChange={setArmConfirm} label="Arm approval" />
              <span className="text-[11px] text-slate-200">I have read the diff &amp; accept blast radius</span>
            </div>
          )}

          {resolved === 'approved' && (
            <div className="mt-3 rounded-sm border border-emerald2-500/40 bg-emerald2-500/[0.06] px-2.5 py-2 font-mono text-[10.5px] text-emerald2-400">
              ✓ promoted by M. Khoury · 14:32:14 · audit log #aud-19842
            </div>
          )}
          {resolved === 'blocked' && (
            <div className="mt-3 rounded-sm border border-crimson2-500/40 bg-crimson2-500/[0.06] px-2.5 py-2 font-mono text-[10.5px] text-crimson2-400">
              ✕ terminated · session agt-9f02 · rollback to PITR 14:31:01 issued
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="border-t border-ink-700/60 p-2.5 grid grid-cols-2 gap-2">
          {resolved === null ? (
            <>
              <Btn
                variant="emerald" size="md" icon="ShieldCheck"
                onClick={onApprove}
                disabled={!armConfirm}
                className={!armConfirm ? 'opacity-50 cursor-not-allowed' : ''}
              >
                Approve &amp; Execute
              </Btn>
              <Btn variant="crimson" size="md" icon="OctagonX" onClick={onBlock}>
                Terminate &amp; Rollback
              </Btn>
            </>
          ) : (
            <Btn variant="ghost" size="md" icon="RotateCcw" onClick={onReset} className="col-span-2">
              Replay intercept · new mutation
            </Btn>
          )}
        </div>
      </div>

      <div className="mt-2 flex items-center justify-between text-[10.5px] font-mono text-slate2-500">
        <span>quorum: 1 of 1</span>
        <span>SLA: 2m · elapsed 0:42</span>
      </div>
    </StageShell>
  );
}

// ──────────────────────── Stage shell ────────────────────────
function StageShell({ idx, title, sub, tone, children }) {
  const tones = {
    azure:   'text-azure2-400   border-azure2-500/30',
    amber:   'text-amber2-400   border-amber2-500/40',
    emerald: 'text-emerald2-400 border-emerald2-500/40',
    crimson: 'text-crimson2-400 border-crimson2-500/40',
  };
  return (
    <div className="relative">
      <div className="flex items-center gap-2 mb-2">
        <span className={`font-mono text-[10px] inline-flex items-center justify-center w-6 h-5 rounded-sm border bg-ink-900 ${tones[tone]}`}>
          {idx}
        </span>
        <div className="leading-tight min-w-0">
          <div className="text-[12.5px] font-semibold text-slate-100 truncate">{title}</div>
          <div className="font-mono text-[10px] text-slate2-500 truncate">{sub}</div>
        </div>
      </div>
      {children}
    </div>
  );
}

window.HarnessPipeline = HarnessPipeline;
