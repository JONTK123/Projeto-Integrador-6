import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Search } from 'lucide-react';
import { getEstabelecimentos, createEstabelecimento, updateEstabelecimento, deleteEstabelecimento, getCategorias } from '../services/api';

export default function Estabelecimentos() {
  const [estabelecimentos, setEstabelecimentos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [estabRes, catRes] = await Promise.all([
        getEstabelecimentos({ limit: 1000 }),
        getCategorias({ limit: 1000 }),
      ]);
      setEstabelecimentos(estabRes.data);
      setCategorias(catRes.data);
    } catch (error) {
      console.error('Erro ao carregar estabelecimentos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      descricao: formData.get('descricao'),
      endereco: formData.get('endereco'),
      cidade: formData.get('cidade'),
      horario_funcionamento: formData.get('horario_funcionamento') || null,
      dono_nome: formData.get('dono_nome') || null,
      dono_email: formData.get('dono_email') || null,
      id_categoria: formData.get('id_categoria') ? parseInt(formData.get('id_categoria')) : null,
    };

    try {
      if (editingItem) {
        await updateEstabelecimento(editingItem.id, data);
      } else {
        await createEstabelecimento(data);
      }
      setShowModal(false);
      setEditingItem(null);
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Erro ao salvar estabelecimento');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Tem certeza que deseja deletar este estabelecimento?')) return;
    try {
      await deleteEstabelecimento(id);
      loadData();
    } catch (error) {
      alert('Erro ao deletar estabelecimento');
    }
  };

  const filtered = estabelecimentos.filter((e) =>
    e.descricao.toLowerCase().includes(search.toLowerCase()) ||
    e.cidade.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="text-center py-8">Carregando...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Estabelecimentos</h1>
        <button
          onClick={() => { setEditingItem(null); setShowModal(true); }}
          className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
        >
          <Plus className="h-5 w-5" />
          <span>Novo Estabelecimento</span>
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar estabelecimentos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{item.descricao}</h3>
              <div className="flex space-x-2">
                <button
                  onClick={() => { setEditingItem(item); setShowModal(true); }}
                  className="text-green-600 hover:text-green-900"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
            <p className="text-sm text-gray-600">{item.endereco}</p>
            <p className="text-sm text-gray-500">{item.cidade}</p>
            {item.horario_funcionamento && (
              <p className="text-xs text-gray-400 mt-2">🕐 {item.horario_funcionamento}</p>
            )}
          </div>
        ))}
      </div>

      {showModal && (
        <Modal title={editingItem ? 'Editar' : 'Novo'} onClose={() => { setShowModal(false); setEditingItem(null); }}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="text" name="descricao" required placeholder="Descrição *" defaultValue={editingItem?.descricao} className="w-full px-3 py-2 border rounded-lg" />
            <input type="text" name="endereco" required placeholder="Endereço *" defaultValue={editingItem?.endereco} className="w-full px-3 py-2 border rounded-lg" />
            <input type="text" name="cidade" required placeholder="Cidade *" defaultValue={editingItem?.cidade} className="w-full px-3 py-2 border rounded-lg" />
            <input type="text" name="horario_funcionamento" placeholder="Horário" defaultValue={editingItem?.horario_funcionamento} className="w-full px-3 py-2 border rounded-lg" />
            <input type="text" name="dono_nome" placeholder="Nome do Dono" defaultValue={editingItem?.dono_nome} className="w-full px-3 py-2 border rounded-lg" />
            <input type="email" name="dono_email" placeholder="Email do Dono" defaultValue={editingItem?.dono_email} className="w-full px-3 py-2 border rounded-lg" />
            <select name="id_categoria" defaultValue={editingItem?.id_categoria} className="w-full px-3 py-2 border rounded-lg">
              <option value="">Categoria</option>
              {categorias.map((c) => <option key={c.id} value={c.id}>{c.nome_categoria}</option>)}
            </select>
            <div className="flex justify-end space-x-3">
              <button type="button" onClick={() => { setShowModal(false); setEditingItem(null); }} className="px-4 py-2 border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg">Salvar</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button onClick={onClose} className="text-gray-500">×</button>
        </div>
        {children}
      </div>
    </div>
  );
}

