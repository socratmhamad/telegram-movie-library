import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import LibraryView from './pages/LibraryView';
import AdminLayout from './components/AdminLayout';
import AdminLibrariesList from './pages/AdminLibrariesList';
import LibraryAdministration from './pages/LibraryAdministration';
import LibrarySettings from './pages/LibrarySettings';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Browsing Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/library/:librarySlug/*" element={<LibraryView />} />
        
        {/* Administration Routes */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="/admin/libraries" replace />} />
          <Route path="libraries" element={<AdminLibrariesList />} />
          <Route path="libraries/:librarySlug" element={<LibraryAdministration />} />
          <Route path="libraries/:librarySlug/settings" element={<LibrarySettings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
