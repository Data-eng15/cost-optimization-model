// Shared low-level UI primitives: Panel, Pill, Btn, Kbd, Sparkline, Toggle

function Panel({ title, eyebrow, children, className = '', actions = null, dense = false }) {
  return (
    <section className={`relative rounded-md border border-ink-700/80 bg-ink-850/60 backdrop-blur ${className}`}>
      {(title || eyebrow || actions) && (
        <header className="flex items-center justify-between px-4 py-2.5 border-b border-ink-700/60">
          <div className="flex items-baseline gap-3 min-w-0">
            {eyebrow && (
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate2-500">
                {eyebrow}
              </span>
            )}
            {title && (
              <h3 className="text-[13px] font-semibold tracking-tight text-slate-100 truncate">
                {title}
              </h3>
            )}
          </div>
          {actions && <div className="flex items-center gap-1.5 shrink-0">{actions}</div>}
        </header>
      )}
      <div className={dense ? '' : 'p-4'}>{children}</div>
    </section>
  );
}

function Pill({ tone = 'slate', children, dot = false, className = '' }) {
  const tones = {
    slate:   'bg-ink-800 text-slate2-300 border-ink-700',
    emerald: 'bg-emerald2-600/15 text-emerald2-400 border-emerald2-600/40',
    amber:   'bg-amber2-500/15   text-amber2-400   border-amber2-500/45',
    crimson: 'bg-crimson2-500/15 text-crimson2-400 border-crimson2-500/45',
    azure:   'bg-azure2-500/15   text-azure2-400   border-azure2-500/40',
  };
  const dotTones = {
    slate: 'bg-slate2-400', emerald: 'bg-emerald2-400',
    amber: 'bg-amber2-400', crimson: 'bg-crimson2-400', azure: 'bg-azure2-400',
  };
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-sm border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider ${tones[tone]} ${className}`}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full pulse-dot ${dotTones[tone]}`} />}
      {children}
    </span>
  );
}

function Btn({ children, variant = 'ghost', size = 'sm', className = '', icon, iconRight, ...rest }) {
  const variants = {
    ghost:   'border border-ink-700 hover:bg-ink-800 text-slate-200',
    solid:   'bg-slate-100 hover:bg-white text-ink-900 border border-slate-100',
    emerald: 'bg-emerald2-600 hover:bg-emerald2-500 text-ink-950 border border-emerald2-500 shadow-glow-emerald',
    crimson: 'bg-crimson2-600 hover:bg-crimson2-500 text-white border border-crimson2-500 shadow-glow-crimson',
    amber:   'bg-amber2-500   hover:bg-amber2-400   text-ink-950 border border-amber2-400',
    outline: 'border border-ink-600 hover:border-ink-500 text-slate-200',
    danger:  'border border-crimson2-600/50 hover:bg-crimson2-600/15 text-crimson2-400',
  };
  const sizes = {
    xs: 'h-6 px-2   text-[11px]   gap-1',
    sm: 'h-7 px-2.5 text-[11.5px] gap-1.5',
    md: 'h-8 px-3   text-xs       gap-1.5',
    lg: 'h-10 px-4  text-sm       gap-2',
  };
  return (
    <button
      className={`inline-flex items-center justify-center rounded-sm font-medium tracking-tight transition-colors ${variants[variant]} ${sizes[size]} ${className}`}
      {...rest}
    >
      {icon && <Icon name={icon} className="w-3.5 h-3.5" />}
      {children}
      {iconRight && <Icon name={iconRight} className="w-3.5 h-3.5" />}
    </button>
  );
}

function Kbd({ children }) {
  return (
    <kbd className="inline-flex items-center justify-center min-w-[1.4em] px-1.5 h-5 rounded-[3px] border border-ink-700 bg-ink-800 font-mono text-[10px] text-slate2-300">
      {children}
    </kbd>
  );
}

// Single-colour sparkline. Pass an array of numbers.
function Sparkline({ data, color = '#5EA8FF', width = 120, height = 32, fill = true }) {
  const min = Math.min(...data), max = Math.max(...data);
  const range = (max - min) || 1;
  const stepX = width / (data.length - 1);
  const points = data.map((v, i) => [
    i * stepX,
    height - ((v - min) / range) * (height - 4) - 2,
  ]);
  const d    = points.map(([x, y], i) => (i === 0 ? `M${x},${y}` : `L${x},${y}`)).join(' ');
  const area = `${d} L${width},${height} L0,${height} Z`;
  const id   = 'sg-' + color.replace('#', '');
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {fill && <path d={area} fill={`url(#${id})`} />}
      <path d={d} fill="none" stroke={color} strokeWidth="1.5"
            strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

// Toggle switch
function Toggle({ on, onChange, disabled = false, label }) {
  return (
    <button
      type="button"
      onClick={() => !disabled && onChange(!on)}
      className={`switch-track relative inline-flex items-center h-5 w-9 rounded-full border
        ${on ? 'bg-emerald2-600/80 border-emerald2-500' : 'bg-ink-800 border-ink-600'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      aria-label={label}
      aria-pressed={on}
    >
      <span className={`switch-thumb absolute top-0.5 left-0.5 w-3.5 h-3.5 rounded-full bg-slate-100 shadow-md ${on ? 'translate-x-4' : ''}`} />
    </button>
  );
}

Object.assign(window, { Panel, Pill, Btn, Kbd, Sparkline, Toggle });
