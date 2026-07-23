import { useState, useEffect } from 'react';
import { formatTelegramUrl } from './TelegramBanner';

function TelegramIcon({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z" />
    </svg>
  );
}

export default function OnboardingModal({ libraryId, telegramChannel, lang }) {
  const [isOpen, setIsOpen] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(true);

  const storageKey = `onboarding_dismissed_${libraryId}`;

  useEffect(() => {
    if (!libraryId) return;
    const isDismissed = localStorage.getItem(storageKey);
    if (!isDismissed) {
      setIsOpen(true);
    }
  }, [libraryId, storageKey]);

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem(storageKey, 'true');
    }
    setIsOpen(false);
  };

  const handleJoin = () => {
    if (dontShowAgain) {
      localStorage.setItem(storageKey, 'true');
    }
    setIsOpen(false);
  };

  if (!isOpen || !telegramChannel) return null;

  const isAr = lang === 'ar';
  const channelUrl = formatTelegramUrl(telegramChannel);

  return (
    <div className="onboarding-overlay" onClick={handleClose}>
      <div
        className="onboarding-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <button
          type="button"
          className="onboarding-modal-close"
          onClick={handleClose}
          aria-label="Close modal"
        >
          ✕
        </button>

        <div className="onboarding-header">
          <div className="onboarding-icon-glow">
            <TelegramIcon size={32} />
          </div>
          <h2 className="onboarding-title">
            {isAr ? 'الانضمام إلى قناة التليجرام' : 'Join the Telegram Channel'}
          </h2>
        </div>

        <div className="onboarding-body">
          <p className="onboarding-message">
            {isAr
              ? 'لفتح روابط الأفلام، يرجى الانضمام إلى قناة التليجرام لهذه المكتبة. إذا كنت قد انضممت بالفعل، يمكنك بدء التصفح مباشرة.'
              : "To open movie links, please join this library's Telegram channel. If you've already joined, simply start browsing."}
          </p>

          <div className="onboarding-checkbox-wrapper">
            <label className="onboarding-checkbox-label">
              <input
                type="checkbox"
                checked={dontShowAgain}
                onChange={(e) => setDontShowAgain(e.target.checked)}
                className="onboarding-checkbox"
              />
              <span>{isAr ? 'عدم الإظهار مرة أخرى' : "Don't show again"}</span>
            </label>
          </div>
        </div>

        <div className="onboarding-footer">
          <a
            href={channelUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="onboarding-btn onboarding-btn-primary"
            onClick={handleJoin}
          >
            <span>🚀</span>
            <span>{isAr ? 'الانضمام للقناة' : 'Join Channel'}</span>
          </a>
          <button
            type="button"
            className="onboarding-btn onboarding-btn-secondary"
            onClick={handleClose}
          >
            {isAr ? 'متابعة التصفح' : 'Continue Browsing'}
          </button>
        </div>
      </div>
    </div>
  );
}
