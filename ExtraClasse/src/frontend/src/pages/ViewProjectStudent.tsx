import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import logo from "../assets/logo2.jpeg";
import { useAuth } from "../contexts/AuthContext";


interface Projeto {
  id: number;
  titulo: string;
  carga_horaria: string;
  duracao: string;
  tipo_projeto: string;
  professor: string;
  financiador: string;
  vagas_voluntarias: number;
  vagas_remuneradas: number;
  descricao: string;
}

interface Aluno {
  id: number;
  Nome: string | undefined;
  status: "Participando" | "Em análise";
}

export default function ViewProjectAluno() {
  const { user } = useAuth();
  const { id } = useParams();
  const [projeto, setProjeto] = useState<Projeto | null>(null);
  const [filtro, setFiltro] = useState("");
  const [alunoLogado] = useState<Aluno>({
    id: 2,
    Nome: user?.nome,
    status: "Em análise", // simula status da API
  });

  useEffect(() => {
    if (!id) return;

    fetch(`http://localhost:8000/api/projetos/${id}/`)
      .then((res) => {
        if (!res.ok) throw new Error("Erro ao buscar projeto");
        return res.json();
      })
      .then((data) => setProjeto(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <main className="w-full h-screen">
      <div className="flex h-full">
        {/* Sidebar de alunos inscritos */}
        <div className="w-64 bg-red-800 flex flex-col gap-6 shadow-lg">
          <div className="flex justify-center items-center bg-white p-2">
            <img src={logo} alt="Logo" className="w-40 h-40 object-contain" />
          </div>
          <h2 className="text-white text-center text-3xl">Meu Status</h2>
          <div className="ml-2 border-2 rounded-2xl border-white p-4 w-11/12 bg-red-900 text-white">
            <p className="text-lg font-semibold">{alunoLogado.Nome}</p>
            <p className="mt-2">
              Status:{" "}
              <span
                className={`px-2 py-1 rounded ${alunoLogado.status === "Participando"
                  ? "bg-green-600"
                  : alunoLogado.status === "Em análise"
                    ? "bg-yellow-500"
                    : "bg-gray-500"
                  }`}
              >
                {alunoLogado.status}
              </span>
            </p>
          </div>
        </div>

        {/* Conteúdo principal */}
        <div className="flex-1 p-6">
          {projeto ? (
            <div className="bg-gray-100 rounded-lg shadow-lg p-6 border border-gray-300 h-full">
              <h1 className="text-3xl font-bold mb-4 text-red-800 text-center">
                {projeto.titulo}
              </h1>

              {/* Grid com informações principais */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">
                    Carga Horária
                  </p>
                  <p className="text-lg font-semibold">
                    {projeto.carga_horaria}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">Duração</p>
                  <p className="text-lg font-semibold">{projeto.duracao}</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">
                    Tipo de Projeto
                  </p>
                  <p className="text-lg font-semibold">
                    {projeto.tipo_projeto}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">
                    Financiador
                  </p>
                  <p className="text-lg font-semibold">{projeto.financiador}</p>
                </div>
                {/* Novo: Professor */}
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">Professor</p>
                  <p className="text-lg font-semibold">{projeto.professor}</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">
                    Vagas Voluntárias
                  </p>
                  <p className="text-lg font-semibold">
                    {projeto.vagas_voluntarias}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">
                    Vagas Remuneradas
                  </p>
                  <p className="text-lg font-semibold">
                    {projeto.vagas_remuneradas}
                  </p>
                </div>
              </div>
              {/* Descrição */}
              <div className="mt-6">
                <p className="text-sm text-gray-500 font-medium">Descrição</p>
                <p className="text-base text-gray-700">{projeto.descricao}</p>
              </div>

              <div className="mt-30 flex gap-4 justify-end">
                <button
                  onClick={() => window.history.back()}
                  className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 transition-colors"
                >
                  Voltar
                </button>
              </div>
            </div>
          ) : (
            <p>Projeto não encontrado.</p>
          )}
        </div>
      </div>
    </main>
  );
}
function setLoading(arg0: boolean): void {
  throw new Error("Function not implemented.");
}
