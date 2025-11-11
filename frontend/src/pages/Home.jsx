import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Building2, Heart, Sparkles, Activity, TrendingUp } from 'lucide-react';
import { getHealth, getUsuarios, getEstabelecimentos, getPreferencias } from '../services/api';

export default function Home() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState({
    usuarios: 0,
    estabelecimentos: 0,
    preferencias: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [healthRes, usuariosRes, estabelecimentosRes, preferenciasRes] = await Promise.all([
        getHealth(),
        getUsuarios({ limit: 1 }),
        getEstabelecimentos({ limit: 1 }),
        getPreferencias({ limit: 1 }),
      ]);

      setHealth(healthRes.data);
      setStats({
        usuarios: usuariosRes.data.length,
        estabelecimentos: estabelecimentosRes.data.length,
        preferencias: preferenciasRes.data.length,
      });
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const cards = [
    {
      title: 'Usuários',
      value: loading ? '...' : stats.usuarios,
      icon: Users,
      color: 'bg-blue-500',
      to: '/usuarios',
    },
    {
      title: 'Estabelecimentos',
      value: loading ? '...' : stats.estabelecimentos,
      icon: Building2,
      color: 'bg-green-500',
      to: '/estabelecimentos',
    },
    {
      title: 'Preferências',
      value: loading ? '...' : stats.preferencias,
      icon: Heart,
      color: 'bg-red-500',
      to: '/preferencias',
    },
    {
      title: 'Recomendações',
      value: 'IA',
      icon: Sparkles,
      color: 'bg-purple-500',
      to: '/recomendacoes',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Sistema de Recomendação
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Plataforma inteligente de recomendações usando LightFM e Surprise para
          conectar usuários aos melhores estabelecimentos
        </p>
      </div>

      {/* Health Status */}
      {health && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className={`h-6 w-6 ${health.status === 'healthy' ? 'text-green-500' : 'text-red-500'}`} />
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Status do Sistema</h2>
                <p className="text-sm text-gray-500">Monitoramento em tempo real</p>
              </div>
            </div>
            <div className="flex space-x-6">
              <StatusBadge label="API" status={health.api === 'online' ? 'success' : 'error'} />
              <StatusBadge label="Database" status={health.database === 'connected' ? 'success' : 'error'} />
              <StatusBadge label="LightFM" status={health.models?.lightfm === 'trained' ? 'success' : 'warning'} />
              <StatusBadge label="Surprise" status={health.models?.surprise === 'trained' ? 'success' : 'warning'} />
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.title}
              to={card.to}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                </div>
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FeatureCard
          icon={TrendingUp}
          title="Algoritmos Avançados"
          description="Utilize LightFM (híbrido CBF+CF) e Surprise (CF puro) para recomendações personalizadas e precisas"
        />
        <FeatureCard
          icon={Sparkles}
          title="Cold Start"
          description="Sistema capaz de fazer recomendações para novos usuários e estabelecimentos sem histórico"
        />
      </div>
    </div>
  );
}

function StatusBadge({ label, status }) {
  const colors = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
  };

  return (
    <div className="text-center">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <span className={`inline-block px-2 py-1 text-xs font-medium rounded ${colors[status]}`}>
        {status === 'success' ? '✓' : status === 'warning' ? '!' : '✗'}
      </span>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start space-x-4">
        <div className="bg-blue-100 p-3 rounded-lg">
          <Icon className="h-6 w-6 text-blue-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-gray-600">{description}</p>
        </div>
      </div>
    </div>
  );
}

