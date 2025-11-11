import { useState, useEffect } from 'react';
import { Sparkles, User, TrendingUp, Zap } from 'lucide-react';
import { getRecomendacoes, getUsuarios, compararAlgoritmos } from '../services/api';

export default function Recomendacoes() {
  const [usuarios, setUsuarios] = useState([]);
  const [selectedUsuario, setSelectedUsuario] = useState('');
  const [recomendacoes, setRecomendacoes] = useState(null);
  const [comparacao, setComparacao] = useState(null);
  const [algoritmo, setAlgoritmo] = useState('lightfm');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUsuarios();
  }, []);

  const loadUsuarios = async () => {
    try {
      const res = await getUsuarios({ limit: 100 });
      setUsuarios(res.data);
    } catch (error) {
      console.error('Erro:', error);
    }
  };

  const buscarRecomendacoes = async () => {
    if (!selectedUsuario) return;
    setLoading(true);
    try {
      const res = await getRecomendacoes(selectedUsuario, { algoritmo, top_n: 10 });
      setRecomendacoes(res.data);
    } catch (error) {
      alert('Erro ao buscar recomendações');
    } finally {
      setLoading(false);
    }
  };

  const buscarComparacao = async () => {
    if (!selectedUsuario) return;
    setLoading(true);
    try {
      const res = await compararAlgoritmos(selectedUsuario, { top_n: 10 });
      setComparacao(res.data);
    } catch (error) {
      alert('Erro ao comparar algoritmos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Recomendações Inteligentes</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 className="text-xl font-semibold flex items-center space-x-2">
          <Sparkles className="h-6 w-6 text-purple-600" />
          <span>Gerar Recomendações</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Usuário</label>
            <select
              value={selectedUsuario}
              onChange={(e) => setSelectedUsuario(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="">Selecione...</option>
              {usuarios.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.nome} ({u.email})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Algoritmo</label>
            <select
              value={algoritmo}
              onChange={(e) => setAlgoritmo(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="lightfm">LightFM (Híbrido)</option>
              <option value="surprise">Surprise (CF)</option>
            </select>
          </div>

          <div className="flex items-end space-x-2">
            <button
              onClick={buscarRecomendacoes}
              disabled={!selectedUsuario || loading}
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300"
            >
              {loading ? 'Gerando...' : 'Recomendar'}
            </button>
            <button
              onClick={buscarComparacao}
              disabled={!selectedUsuario || loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
            >
              Comparar
            </button>
          </div>
        </div>
      </div>

      {recomendacoes && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            Recomendações - {recomendacoes.algoritmo}
          </h3>
          <div className="space-y-3">
            {recomendacoes.recomendacoes.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="font-medium">{item.estabelecimento_nome}</div>
                  <div className="text-sm text-gray-600">{item.cidade}</div>
                  {item.razao && <div className="text-xs text-gray-500 mt-1">{item.razao}</div>}
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-600">
                    {(item.score * 10).toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-500">score</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {comparacao && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              <span>LightFM</span>
            </h3>
            <div className="space-y-2">
              {comparacao.lightfm.map((item, idx) => (
                <div key={idx} className="p-3 bg-yellow-50 rounded-lg">
                  <div className="font-medium text-sm">{item.estabelecimento_nome}</div>
                  <div className="text-xs text-gray-600">Score: {(item.score * 10).toFixed(1)}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-blue-500" />
              <span>Surprise</span>
            </h3>
            <div className="space-y-2">
              {comparacao.surprise.map((item, idx) => (
                <div key={idx} className="p-3 bg-blue-50 rounded-lg">
                  <div className="font-medium text-sm">{item.estabelecimento_nome}</div>
                  <div className="text-xs text-gray-600">Score: {(item.score * 10).toFixed(1)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

