import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import icon from "../assets/icon.svg";

interface Aluno {
  id: number;
  nome: string; // igual ao campo no backend
  matricula: string;
  email: string;
  coeficiente: string;
  curso: string;
}

export default function StudentInfo() {
  const { nome } = useParams<{ id?: string; nome?: string }>();
  const [aluno, setAluno] = useState<Aluno | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!nome) return;

    const nomeDecodificado = decodeURIComponent(nome);

    fetch(`http://localhost:8000/api/alunos/busca/?nome=${nomeDecodificado}`)
      .then((res) => {
        if (!res.ok) throw new Error("Aluno não encontrado");
        return res.json();
      })
      .then((data: Aluno | Aluno[]) => {
        if (Array.isArray(data)) setAluno(data[0] || null);
        else setAluno(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [nome]);

  if (loading) return <p className="text-center mt-16">Carregando...</p>;
  if (error || !aluno)
    return (
      <p className="text-center mt-16">{error || "Aluno não encontrado."}</p>
    );

  return (
    <main className="flex justify-center bg-white min-h-screen">
      <div className="max-w-4xl w-full p-6 bg-white border">
        {/* Avatar */}
        <div className="flex justify-center items-center mb-8 mt-16">
          <img
            src={icon}
            alt="aluno"
            className="w-40 h-40 rounded-full shadow bg-gray-500 object-cover"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-500 font-medium">Nome</p>
            <p className="text-lg font-semibold">{aluno.nome}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-500 font-medium">Matrícula</p>
            <p className="text-lg font-semibold">{aluno.matricula}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-500 font-medium">Email</p>
            <p className="text-lg font-semibold">{aluno.email}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-500 font-medium">Curso</p>
            <p className="text-lg font-semibold">{aluno.curso}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-500 font-medium">Coeficiente</p>
            <p className="text-lg font-semibold">{aluno.coeficiente}</p>
          </div>
        </div>

        <div className="flex justify-end gap-4 mt-6">
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition-colors"
          >
            Voltar
          </button>

          <button
            onClick={() => alert(`Aluno ${aluno.nome} aprovado!`)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Aprovar Aluno
          </button>
        </div>
      </div>
    </main>
  );
}
