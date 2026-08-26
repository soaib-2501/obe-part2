import React from 'react';

export function a4TableBlocks({ title, head, rows, footer }) {
  const list = rows?.length ? rows : [null];
  return list.map((row, index) => (
    <div key={title ? `${title}-${index}` : index} className={index === 0 ? 'a4-block' : 'a4-block a4-block-cont'}>
      {index === 0 && title ? <h3>{title}</h3> : null}
      <table>
        {head ? <thead>{head}</thead> : null}
        <tbody>
          {row}
          {footer && index === list.length - 1 ? footer : null}
        </tbody>
      </table>
    </div>
  ));
}
