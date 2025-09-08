// src/pages/DeleteProject.tsx
import { useParams, useNavigate } from "react-router-dom";

export default function DeleteProject() {
  const { id } = useParams();
  const navigate = useNavigate();

  const handleDelete = async () => {
    const res = await fetch(`http://localhost:8000/api/projetos/${id}/`, {
      method: "DELETE",
    });

    if (res.ok) {
      alert("Projeto deletado com sucesso!");
      navigate("/dashboard"); // redireciona para a lista
    } else {
      alert("Erro ao deletar projeto");
    }
  };

  return (
    <main className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-2xl font-bold mb-4">Excluir Projeto?</h1>
      <p className="mb-6">Tem certeza que deseja excluir o projeto {id}?</p>
      <div className="flex gap-4">
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 bg-gray-300 rounded"
        >
          Cancelar
        </button>
        <button
          onClick={handleDelete}
          className="px-4 py-2 bg-red-600 text-white rounded"
        >
          Confirmar
        </button>
      </div>
    </main>
  );
}
