import { useState } from 'react';
import { BookOpen, Play, CheckCircle, XCircle } from 'lucide-react';
import { treinarModelo } from '../services/api';

export default function Treinamento() {
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);

  const treinar = async (algoritmo) => {
    setLoading(true);
    setResultado(null);
    try {
      const data = {
        algoritmo,
        loss: 'warp',
        usar_features: true,
        algorithm: 'SVD',
        num_epochs: 30,
      };
      const res = await treinarModelo(data);
      setResultado({ success: true, data: res.data });
    } catch (error) {
      setResultado({ success: false, error: error.response?.data?.detail || 'Erro' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Treinamento de Modelos</h1>
        <p className="text-gray-600 mt-2">Treine os modelos de recomendação com dados atualizados</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-yellow-100 p-3 rounded-lg">
              <BookOpen className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">LightFM</h2>
              <p className="text-sm text-gray-600">Híbrido (CBF + CF)</p>
            </div>
          </div>
          <p className="text-gray-600 mb-4 text-sm">
            Modelo híbrido que combina Collaborative Filtering e Content-Based Filtering.
            Usa features de usuários e estabelecimentos para recomendações precisas.
          </p>
          <button
            onClick={() => treinar('lightfm')}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 bg-yellow-600 text-white px-4 py-3 rounded-lg hover:bg-yellow-700 disabled:bg-gray-300"
          >
            <Play className="h-5 w-5" />
            <span>{loading ? 'Treinando...' : 'Treinar LightFM'}</span>
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <BookOpen className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Surprise</h2>
              <p className="text-sm text-gray-600">Collaborative Filtering</p>
            </div>
          </div>
          <p className="text-gray-600 mb-4 text-sm">
            Biblioteca especializada em algoritmos de CF. Usa apenas padrões de
            comportamento (interações) para gerar recomendações.
          </p>
          <button
            onClick={() => treinar('surprise')}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
          >
            <Play className="h-5 w-5" />
            <span>{loading ? 'Treinando...' : 'Treinar Surprise'}</span>
          </button>
        </div>
      </div>

      {resultado && (
        <div className={`rounded-lg p-6 ${resultado.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-start space-x-3">
            {resultado.success ? (
              <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
            ) : (
              <XCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
            )}
            <div className="flex-1">
              <h3 className="font-semibold mb-2">
                {resultado.success ? 'Treinamento Concluído!' : 'Erro no Treinamento'}
              </h3>
              {resultado.success && resultado.data && (
                <div className="space-y-2">
                  <p className="text-sm">{resultado.data.message}</p>
                  {resultado.data.metricas && (
                    <div className="bg-white rounded p-3 text-sm">
                      <strong>Métricas:</strong>
                      <pre className="mt-2 text-xs">{JSON.stringify(resultado.data.metricas, null, 2)}</pre>
                    </div>
                  )}
                </div>
              )}
              {!resultado.success && (
                <p className="text-sm text-red-600">{resultado.error}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

