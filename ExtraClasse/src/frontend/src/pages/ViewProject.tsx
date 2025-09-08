import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import logo from "../assets/logo2.jpeg";

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
  alunos: Aluno[];
}

interface Aluno {
  id: number;
  nome: string; // cuidado com o campo do backend, se for 'nome'
  status?: "Participando" | "Em análise"; // opcional, se tiver
}

export default function ViewProject() {
  const { id } = useParams();
  const [projeto, setProjeto] = useState<Projeto | null>(null);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState("");

  useEffect(() => {
    if (!id) return;

    setLoading(true);

    fetch(`http://localhost:8000/api/projetos/${id}/`)
      .then((res) => {
        if (!res.ok) throw new Error("Erro ao buscar projeto");
        return res.json();
      })
      .then((data: Projeto) => setProjeto(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  const alunosFiltrados =
    projeto?.alunos.filter((aluno) =>
      aluno.nome.toLowerCase().startsWith(filtro.toLowerCase())
    ) || [];

  if (loading) return <p>Carregando...</p>;

  return (
    <main className="w-full h-screen">
      <div className="flex h-full">
        {/* Sidebar alunos */}
        <div className="w-64 bg-red-800 flex flex-col gap-6 shadow-lg">
          <div className="flex justify-center items-center bg-white p-2">
            <img src={logo} alt="Logo" className="w-40 h-40 object-contain" />
          </div>
          <div className="mt-6">
            <p className="text-sm text-gray-200 font-medium mb-2 text-center">
              Alunos Inscritos
            </p>

            <input
              type="text"
              placeholder="Buscar aluno..."
              className="border border-white bg-red-700 px-4 py-2 rounded-lg w-full text-white placeholder-white mb-4 focus:outline-none focus:ring-2 focus:ring-white transition"
              value={filtro}
              onChange={(e) => setFiltro(e.target.value)}
            />

            {projeto && projeto.alunos.length > 0 ? (
              <ul className="max-h-64 overflow-y-auto flex flex-col gap-1">
                {projeto.alunos
                  .filter((aluno) =>
                    aluno.nome.toLowerCase().startsWith(filtro.toLowerCase())
                  )
                  .map((aluno) => (
                    <Link
                      to={`/dashboard/studentinfo/${encodeURIComponent(
                        aluno.nome
                      )}`}
                      key={aluno.id}
                      className="block p-3 bg-red-700 hover:bg-red-600 rounded-lg text-white font-medium transition"
                    >
                      {aluno.nome}
                    </Link>
                  ))}
              </ul>
            ) : (
              <p className="text-gray-300">Nenhum aluno inscrito.</p>
            )}
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
                  <p className="text-sm text-gray-500 font-medium">Professor</p>
                  <p className="text-lg font-semibold">{projeto.professor}</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-500 font-medium">
                    Financiador
                  </p>
                  <p className="text-lg font-semibold">{projeto.financiador}</p>
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
                <Link
                  to={`/dashboard/projetos/${id}/delete`}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-500 transition"
                >
                  Deletar
                </Link>
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
