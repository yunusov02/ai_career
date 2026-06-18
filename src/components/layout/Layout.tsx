import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';

export function Layout() {
  return (
    <div className="min-h-screen bg-[#f7f8f4] text-slate-950">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <footer className="mt-auto border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-7 text-sm text-slate-500 lg:px-8">
          <span className="font-semibold text-slate-700">SkillBridge</span>
          <span>© 2026</span>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
