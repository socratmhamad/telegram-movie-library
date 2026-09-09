import { useState, useEffect } from 'react';

export default function TypewriterTitle({ lang = 'en' }) {
  const isAr = lang === 'ar';
  const targetText = isAr ? 'مكتبة أفلام التليغرام' : 'Telegram Movies Library';

  const [text, setText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    // Reset immediately when language changes
    setText('');
    setIsDeleting(false);
  }, [targetText]);

  useEffect(() => {
    let timer;

    if (!isDeleting) {
      // Typing phase: ~80ms per character
      if (text.length < targetText.length) {
        timer = setTimeout(() => {
          setText(targetText.slice(0, text.length + 1));
        }, 80);
      } else {
        // Full text reached: pause 2.5s (2500ms) for reading
        timer = setTimeout(() => {
          setIsDeleting(true);
        }, 2500);
      }
    } else {
      // Deleting phase: ~40ms per character
      if (text.length > 0) {
        timer = setTimeout(() => {
          setText(targetText.slice(0, text.length - 1));
        }, 40);
      } else {
        // Empty text reached: pause 0.5s (500ms) before retyping
        timer = setTimeout(() => {
          setIsDeleting(false);
        }, 500);
      }
    }

    return () => clearTimeout(timer);
  }, [text, isDeleting, targetText]);

  return (
    <span className={`header-typewriter-title ${isAr ? 'ar' : 'en'}`} aria-label={targetText}>
      <span className="typewriter-text">{text}</span>
      <span className="typewriter-cursor" aria-hidden="true">|</span>
    </span>
  );
}
