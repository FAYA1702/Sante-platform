import React, { useState } from 'react';

interface CreateRecommandationModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (values: { user_id: string; titre: string; description: string }) => void;
  patient?: { id: string; username: string };
  alerte?: { message: string };
}

const CreateRecommandationModal: React.FC<CreateRecommandationModalProps> = ({ open, onClose, onSubmit, patient, alerte }) => {
  const [titre, setTitre] = useState('');
  const [description, setDescription] = useState('');

  React.useEffect(() => {
    if (alerte) {
      setTitre(alerte.message.includes('Tachycardie') ? '⚠️ Surveillance cardiaque' :
        alerte.message.includes('Hypoxie') ? '🚑 Surveillance respiratoire urgente' :
        'Recommandation médicale');
      setDescription(alerte.message);
    } else {
      setTitre('Recommandation médicale');
      setDescription('');
    }
  }, [alerte, open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-lg p-8 relative">
        <button
          className="absolute top-3 right-3 text-gray-500 hover:text-red-500"
          onClick={onClose}
        >
          ✕
        </button>
        <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Créer une recommandation</h2>
        <form
          onSubmit={e => {
            e.preventDefault();
            if (!patient) return;
            onSubmit({ user_id: patient.id, titre, description });
          }}
        >
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Patient</label>
            <input
              type="text"
              value={patient ? patient.username : ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Titre</label>
            <input
              type="text"
              value={titre}
              onChange={e => setTitre(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded"
            />
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded"
            />
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-5 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold"
            >
              Créer
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateRecommandationModal;
