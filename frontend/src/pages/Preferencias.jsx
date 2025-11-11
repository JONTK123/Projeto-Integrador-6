import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Heart } from 'lucide-react';
import { getPreferencias, createPreferencia, updatePreferencia, deletePreferencia } from '../services/api';

export default function Preferencias() {
  const [preferencias, setPreferencias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await getPreferencias({ limit: 1000 });
      setPreferencias(res.data);
    } catch (error) {
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      nome_preferencia: formData.get('nome_preferencia'),
      tipo_preferencia: formData.get('tipo_preferencia'),
    };

    try {
      if (editingItem) {
        await updatePreferencia(editingItem.id, data);
      } else {
        await createPreferencia(data);
      }
      setShowModal(false);
      setEditingItem(null);
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Erro ao salvar');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Deletar?')) return;
    try {
      await deletePreferencia(id);
      loadData();
    } catch (error) {
      alert('Erro ao deletar');
    }
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Preferências</h1>
        <button onClick={() => { setEditingItem(null); setShowModal(true); }} className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg">
          <Plus className="h-5 w-5" />
          <span>Nova Preferência</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {preferencias.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <Heart className="h-5 w-5 text-red-500" />
                  <h3 className="font-semibold text-gray-900">{item.nome_preferencia}</h3>
                </div>
                <span className="inline-block px-2 py-1 text-xs bg-red-100 text-red-800 rounded">{item.tipo_preferencia}</span>
              </div>
              <div className="flex flex-col space-y-1">
                <button onClick={() => { setEditingItem(item); setShowModal(true); }} className="text-red-600">
                  <Edit className="h-4 w-4" />
                </button>
                <button onClick={() => handleDelete(item.id)} className="text-gray-600">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <Modal title={editingItem ? 'Editar' : 'Nova'} onClose={() => { setShowModal(false); setEditingItem(null); }}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="text" name="nome_preferencia" required placeholder="Nome *" defaultValue={editingItem?.nome_preferencia} className="w-full px-3 py-2 border rounded-lg" />
            <input type="text" name="tipo_preferencia" required placeholder="Tipo *" defaultValue={editingItem?.tipo_preferencia} className="w-full px-3 py-2 border rounded-lg" />
            <div className="flex justify-end space-x-3">
              <button type="button" onClick={() => { setShowModal(false); setEditingItem(null); }} className="px-4 py-2 border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 bg-red-600 text-white rounded-lg">Salvar</button>
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
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button onClick={onClose}>×</button>
        </div>
        {children}
      </div>
    </div>
  );
}

