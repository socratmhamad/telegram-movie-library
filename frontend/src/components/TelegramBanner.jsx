import { useState } from 'react';

function TelegramIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z" />
    </svg>
  );
}

export function formatTelegramUrl(channel) {
  if (!channel) return '#';
  const url = channel.trim();
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  if (url.startsWith('@')) {
    return `https://t.me/${url.slice(1)}`;
  }
  if (url.startsWith('t.me/')) {
    return `https://${url}`;
  }
  return `https://t.me/${url}`;
}

export default function TelegramBanner({ telegramChannel, lang }) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !telegramChannel) return null;

  const isAr = lang === 'ar';
  const channelUrl = formatTelegramUrl(telegramChannel);

  return (
    <div className="telegram-sticky-banner">
      <div className="telegram-banner-content">
        <div className="telegram-banner-info">
          <span className="telegram-banner-badge">
            <TelegramIcon size={18} />
          </span>
          <span className="telegram-banner-text">
            {isAr
              ? 'انضم إلى القناة للوصول إلى روابط الأفلام.'
              : 'Join the channel to access movie links.'}
          </span>
        </div>
        <div className="telegram-banner-actions">
          <a
            href={channelUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="telegram-banner-btn"
          >
            <TelegramIcon size={16} />
            <span>{isAr ? 'انضمام للقناة' : 'Join Channel'}</span>
          </a>
          <button
            type="button"
            className="telegram-banner-close"
            onClick={() => setDismissed(true)}
            aria-label="Dismiss banner"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}
