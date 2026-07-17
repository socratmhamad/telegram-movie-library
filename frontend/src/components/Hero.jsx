import { useState, useEffect, useCallback } from 'react';

const HERO_MOVIES = [
  {
    id: 'interstellar',
    backdrop: 'https://image.tmdb.org/t/p/original/2ssWTSVklAEc98frZUQhgtGHx7s.jpg',
    poster: 'https://image.tmdb.org/t/p/w500/yQvGrMoipbRoddT0ZR8tPoR7NfX.jpg',
    rating: 8.4,
    year: 2014,
    en: {
      title: 'Interstellar',
      tagline: 'Sci-Fi • Adventure • Drama',
      overview: 'The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.'
    },
    ar: {
      title: 'بين النجوم',
      tagline: 'خيال علمي • مغامرة • دراما',
      overview: 'تتتبع القصة مغامرات مجموعة من المستكشفين الذين يسافرون عبر ثقب دودي تم اكتشافه حديثاً في محاولة لتأمين بقاء البشرية وتجاوز حدود السفر البشري عبر الفضاء.'
    }
  },
  {
    id: 'dark-knight',
    backdrop: 'https://image.tmdb.org/t/p/original/dqK9Hag1054tghRQSqLSfrkvQnA.jpg',
    poster: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
    rating: 9.0,
    year: 2008,
    en: {
      title: 'The Dark Knight',
      tagline: 'Action • Crime • Drama',
      overview: 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.'
    },
    ar: {
      title: 'فارس الظلام',
      tagline: 'حركة • جريمة • دراما',
      overview: 'عندما يبدأ الجوكر في نشر الفوضى والدمار في مدينة غوثام، يجب على باتمان مواجهة أحد أعظم الاختبارات النفسية والجسدية لقدرته على محاربة الظلم.'
    }
  },
  {
    id: 'godfather',
    backdrop: 'https://image.tmdb.org/t/p/original/tSPT36ZKlP2WVHJLM4cQPLSzv3b.jpg',
    poster: 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
    rating: 9.2,
    year: 1972,
    en: {
      title: 'The Godfather',
      tagline: 'Crime • Drama',
      overview: 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone, survives an attempt on his life, his youngest son, Michael, steps in to take care of the would-be killers.'
    },
    ar: {
      title: 'العراب',
      tagline: 'جريمة • دراما',
      overview: 'يروي الفيلم قصة عائلة كورليوني الخيالية الشهيرة في الفترة من 1945 إلى 1955. بعد نجاة الأب فيتو كورليوني من محاولة اغتيال، يتدخل ابنه الأصغر مايكل للانتقام وحماية العائلة.'
    }
  },
  {
    id: 'shawshank',
    backdrop: 'https://image.tmdb.org/t/p/original/zfbjgQE1uSd9wiPTX4VzsLi0rGG.jpg',
    poster: 'https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg',
    rating: 9.3,
    year: 1994,
    en: {
      title: 'The Shawshank Redemption',
      tagline: 'Drama',
      overview: 'Imprisoned in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden.'
    },
    ar: {
      title: 'خلاص شاوشانك',
      tagline: 'دراما',
      overview: 'سجين يُحكم عليه بالمؤبد في الأربعينيات بتهمة قتل زوجته وعشيقها، ويبدأ حياة جديدة في سجن شاوشانك القاسي، حيث يستخدم مهاراته الحسابية لمساعدة مدير السجن الفاسد وكسب ود الحراس.'
    }
  },
  {
    id: 'inception',
    backdrop: 'https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg',
    poster: 'https://image.tmdb.org/t/p/w500/xlaY2zyzMfkhk0HSC5VUwzoZPU1.jpg',
    rating: 8.3,
    year: 2010,
    en: {
      title: 'Inception',
      tagline: 'Action • Sci-Fi • Adventure',
      overview: 'Cobb, a skilled thief who commits subconscious espionage by entering the dreams of others, is given a single last chance to regain his old life as payment for a task considered to be impossible: "inception".'
    },
    ar: {
      title: 'استهلال',
      tagline: 'حركة • خيال علمي • مغامرة',
      overview: 'عميل سري متخصص في سرقة الأفكار من العقول الباطنة للآخرين أثناء نومهم، يُمنح فرصة أخيرة لاستعادة حياته السابقة مقابل تنفيذ مهمة مستحيلة وهي زرع فكرة داخل عقل شخص ما.'
    }
  }
];

export default function Hero({ lang = 'en', onSelectLibrary }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const isAr = lang === 'ar';

  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % HERO_MOVIES.length);
    }, 6000);
    return () => clearInterval(interval);
  }, [isPaused]);

  const handlePrev = useCallback(() => {
    setCurrentIndex((prev) => (prev - 1 + HERO_MOVIES.length) % HERO_MOVIES.length);
  }, []);

  const handleNext = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % HERO_MOVIES.length);
  }, []);

  const scrollToLibraries = useCallback(() => {
    const section = document.querySelector('.library-landing');
    if (section) {
      const headerOffset = 80;
      const elementPosition = section.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  }, []);

  const movie = HERO_MOVIES[currentIndex];
  const t = isAr ? movie.ar : movie.en;

  return (
    <div
      className="hero-slider"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Background Backdrops */}
      {HERO_MOVIES.map((m, idx) => (
        <div
          key={m.id}
          className={`hero-slide ${idx === currentIndex ? 'active' : ''}`}
          style={{ backgroundImage: `url(${m.backdrop})` }}
        />
      ))}

      {/* Dark Overlays (linear & radial) */}
      <div className="hero-gradient-left" />
      <div className="hero-gradient-bottom" />

      {/* Content */}
      <div className="hero-content" key={currentIndex}>
        <div className="hero-meta-badge">
          <span className="hero-badge-rating">★ {movie.rating.toFixed(1)}</span>
          <span className="hero-badge-divider">|</span>
          <span className="hero-badge-year">{movie.year}</span>
        </div>
        <h1 className="hero-title">{t.title}</h1>
        <p className="hero-tagline">{t.tagline}</p>
        <p className="hero-overview">{t.overview}</p>

        <div className="hero-actions">
          <button className="hero-btn-primary" onClick={scrollToLibraries}>
            🍿 {isAr ? 'استكشف المكتبات' : 'Explore Libraries'}
          </button>
        </div>
      </div>

      {/* Slide Navigation Controls */}
      <button 
        className="hero-nav-arrow prev" 
        onClick={handlePrev} 
        aria-label={isAr ? 'السابق' : 'Previous Slide'}
      >
        {isAr ? '→' : '←'}
      </button>
      <button 
        className="hero-nav-arrow next" 
        onClick={handleNext} 
        aria-label={isAr ? 'التالي' : 'Next Slide'}
      >
        {isAr ? '←' : '→'}
      </button>

      {/* Indicator Bullets */}
      <div className="hero-bullets">
        {HERO_MOVIES.map((_, idx) => (
          <button
            key={idx}
            className={`hero-bullet ${idx === currentIndex ? 'active' : ''}`}
            onClick={() => setCurrentIndex(idx)}
            aria-label={`Slide ${idx + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
