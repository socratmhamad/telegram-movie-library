import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function PublicLayout({ children }) {
  return (
    <div className="public-layout">
      <header className="public-header">
        <div className="public-header-inner">
          <Link to="/" className="public-logo" id="app-logo">
            <span className="public-logo-icon">🎬</span>
            مكتبة الأفلام
          </Link>
        </div>
      </header>
      <motion.main
        className="public-main"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.main>
    </div>
  );
}
