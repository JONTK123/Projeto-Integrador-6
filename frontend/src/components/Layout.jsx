import { Link, Outlet, useLocation } from 'react-router-dom';
import { Home, Users, Building2, Heart, Sparkles, BookOpen } from 'lucide-react';
import { cn } from '../lib/cn';

const navigation = [
  { name: 'Home', to: '/', icon: Home },
  { name: 'Usuários', to: '/usuarios', icon: Users },
  { name: 'Estabelecimentos', to: '/estabelecimentos', icon: Building2 },
  { name: 'Preferências', to: '/preferencias', icon: Heart },
  { name: 'Recomendações', to: '/recomendacoes', icon: Sparkles },
  { name: 'Treinamento', to: '/treinamento', icon: BookOpen },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Sparkles className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">
                  Sistema de Recomendação
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.to;
                  return (
                    <Link
                      key={item.name}
                      to={item.to}
                      className={cn(
                        'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium',
                        isActive
                          ? 'border-blue-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      )}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Sistema de Recomendação - LightFM & Surprise
          </p>
        </div>
      </footer>
    </div>
  );
}

