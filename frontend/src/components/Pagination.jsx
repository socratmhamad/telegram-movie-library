import { useMemo } from 'react';

export default function Pagination({ page, totalPages, total, onPageChange }) {
  const pages = useMemo(() => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const items = [];
    items.push(1);

    if (page > 3) items.push('…');

    const start = Math.max(2, page - 1);
    const end = Math.min(totalPages - 1, page + 1);
    for (let i = start; i <= end; i++) items.push(i);

    if (page < totalPages - 2) items.push('…');
    items.push(totalPages);

    return items;
  }, [page, totalPages]);

  if (totalPages <= 1) return null;

  return (
    <nav className="pagination" id="pagination" aria-label="التنقل بين الصفحات">
      <button
        className="pagination-btn"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="الصفحة السابقة"
      >
        ‹
      </button>

      {pages.map((p, idx) =>
        p === '…' ? (
          <span key={`e${idx}`} className="pagination-ellipsis">…</span>
        ) : (
          <button
            key={p}
            className={`pagination-btn ${p === page ? 'active' : ''}`}
            onClick={() => onPageChange(p)}
            aria-current={p === page ? 'page' : undefined}
          >
            {p}
          </button>
        )
      )}

      <button
        className="pagination-btn"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="الصفحة التالية"
      >
        ›
      </button>

      <span className="pagination-info">
        {total.toLocaleString('ar-EG')} {total === 1 ? 'فيلم' : 'أفلام'}
      </span>
    </nav>
  );
}
