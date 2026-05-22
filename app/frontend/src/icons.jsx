// Lucide icon shortcut — reads icon data from the `lucide` global (UMD)
// and renders to a React <svg>. Usage: <Icon name="Activity" className="w-4 h-4" />

const LUCIDE = window.lucide || {};
const ICONS  = (LUCIDE && LUCIDE.icons) || {};

function toAttrs(o, extra = {}) {
  const out = {};
  for (const k in o) {
    if      (k === 'stroke-width')   out.strokeWidth   = o[k];
    else if (k === 'stroke-linecap') out.strokeLinecap  = o[k];
    else if (k === 'stroke-linejoin')out.strokeLinejoin = o[k];
    else if (k === 'class')          out.className      = o[k];
    else out[k] = o[k];
  }
  Object.assign(out, extra);
  return out;
}

function renderNode([tag, attrs, kids], key) {
  const children = Array.isArray(kids) ? kids.map((c, i) => renderNode(c, i)) : null;
  return React.createElement(tag, { ...toAttrs(attrs), key }, children);
}

function Icon({ name, className = 'w-4 h-4', strokeWidth = 1.75, color, ...rest }) {
  const data = ICONS[name] || LUCIDE[name];
  if (!data) {
    return (
      <span
        className={className}
        style={{ display: 'inline-block', background: 'currentColor', opacity: 0.35, borderRadius: 2 }}
      />
    );
  }
  const [, rootAttrs, kids] = data;
  const attrs = toAttrs(rootAttrs, {
    className,
    strokeWidth,
    ...(color ? { stroke: color } : {}),
    'aria-hidden': true,
    ...rest,
  });
  delete attrs.width;
  delete attrs.height;
  return React.createElement('svg', attrs, kids.map((c, i) => renderNode(c, i)));
}

window.Icon = Icon;
