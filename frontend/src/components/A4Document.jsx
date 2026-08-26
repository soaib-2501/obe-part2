import React, { useLayoutEffect, useMemo, useRef, useState } from 'react';

function flattenChildren(children) {
  const out = [];
  React.Children.forEach(children, (child) => {
    if (child == null || child === false) return;
    if (child.type === React.Fragment) {
      out.push(...flattenChildren(child.props.children));
    } else {
      out.push(child);
    }
  });
  return out;
}

export default function A4Document({ revision, watermark, sheetClass = '', children }) {
  const items = useMemo(() => flattenChildren(children), [children]);
  const measureRef = useRef(null);
  const probeRef = useRef(null);
  const stageRef = useRef(null);
  const [groups, setGroups] = useState([]);
  const [scale, setScale] = useState(1);

  useLayoutEffect(() => {
    let cancelled = false;
    const run = () => {
      if (cancelled) return;
      const probe = probeRef.current;
      const root = measureRef.current;
      const stage = stageRef.current;
      if (!probe || !root) return;

      const pagePx = probe.offsetHeight;
      const pageW = probe.offsetWidth;
      const padTop = parseFloat(getComputedStyle(root).paddingTop) || 0;
      const padBottom = parseFloat(getComputedStyle(root).paddingBottom) || 0;
      const maxH = Math.max(80, pagePx - padTop - padBottom - 8);

      const nodes = [...root.querySelectorAll(':scope > .doc-body > .a4-measure-item')];
      const packed = [];
      let current = [];
      let used = 0;
      nodes.forEach((node, index) => {
        const height = Math.ceil(node.getBoundingClientRect().height);
        const next = nodes[index + 1];
        const keepNext = !!(node.classList.contains('a4-keep-next') || node.querySelector(':scope > .a4-keep-next'));
        const nextH = keepNext && next ? Math.ceil(next.getBoundingClientRect().height) : 0;
        const pairFitsPage = height + nextH <= maxH;
        const pairOverflows = nextH > 0 && pairFitsPage && used + height + nextH > maxH;
        if (current.length > 0 && (used + height > maxH || pairOverflows)) {
          packed.push(current);
          current = [index];
          used = height;
        } else {
          current.push(index);
          used += height;
        }
      });
      if (current.length) packed.push(current);
      const nextGroups = packed.length ? packed : [];
      setGroups((prev) => (JSON.stringify(prev) === JSON.stringify(nextGroups) ? prev : nextGroups));

      if (stage && pageW > 0) {
        const available = stage.clientWidth - 24;
        const nextScale = available > 0 ? Math.min(1, available / pageW) : 1;
        setScale((prev) => (Math.abs(prev - nextScale) < 0.001 ? prev : nextScale));
      }
    };

    const id = window.requestAnimationFrame(() => window.requestAnimationFrame(run));
    window.addEventListener('resize', run);
    return () => {
      cancelled = true;
      window.cancelAnimationFrame(id);
      window.removeEventListener('resize', run);
    };
  }, [revision, items.length]);

  const pages = groups.length ? groups : [items.map((_, i) => i)];
  const pageCount = Math.max(pages.length, 1);
  const gap = 20;

  return (
    <div className="a4-stage" ref={stageRef}>
      <div className="a4-page-probe" ref={probeRef} aria-hidden="true" />
      <div className={`a4-measure-root page ${sheetClass}`.trim()} ref={measureRef} aria-hidden="true">
        <div className="doc-body">
          {items.map((child, i) => (
            <div key={`m-${i}`} className="a4-measure-item">{child}</div>
          ))}
        </div>
      </div>

      <div
        className="a4-scale-outer"
        style={{
          height: `calc((${pageCount} * 297mm + ${(pageCount - 1) * gap}px) * ${scale})`,
          width: `calc(210mm * ${scale})`,
        }}
      >
        <div className="a4-scale-inner" style={{ transform: `scale(${scale})` }}>
          <div className="a4-wrap a4-paged">
            {pages.map((indexes, pageIndex) => (
              <section key={`page-${pageIndex}`} className={`page a4-sheet ${sheetClass}`.trim()}>
                {watermark ? (
                  <div className="watermark-layer" aria-hidden="true"><span>{watermark}</span></div>
                ) : null}
                <div className="doc-body">
                  {indexes.map((i) => (
                    <React.Fragment key={`c-${pageIndex}-${i}`}>{items[i]}</React.Fragment>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
