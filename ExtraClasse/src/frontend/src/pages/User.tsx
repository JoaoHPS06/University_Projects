// Em: src/pages/User.tsx

import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";
import { useState, useEffect } from "react";

interface Projeto {
  id: number;
  titulo: string;
  carga_horaria: string; // Mantendo como string, conforme seu serializer
  duracao: string;
  professor: string;
  tipo_projeto: string;
}

export default function UserDashboard() {
  const { user } = useAuth();

  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [isLoading, setIsLoading] = useState(true); // Inicia como true
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjetos = async () => {
      if (!user) return;

      setIsLoading(true);
      setError(null);

      try {
        let url = "";

        if (user.tipo_usuario === "professor") {
          // URL para professor (projetos que ele cadastrou)
          const professorNome = encodeURIComponent(user.nome);
          url = `http://127.0.0.1:8000/api/projetos/?professor=${professorNome}`;
        } else if (user.tipo_usuario === "aluno") {
          // URL para aluno (projetos em que está inscrito)
          url = `http://127.0.0.1:8000/api/projetos/aluno/?aluno_nome=${user.nome}`;
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error("Erro ao buscar projetos");
        const data = await response.json();
        setProjetos(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjetos();
  }, [user]);

  // Verificação inicial do usuário (do seu código original)
  if (!user) {
    return <div>Carregando informações do usuário...</div>;
  }

  // ✅ 5. Adicionar renderização para os estados de carregamento e erro.
  if (isLoading) {
    return <div>Carregando projetos...</div>;
  }

  if (error) {
    return (
      <div className="p-6 text-red-600">Erro ao carregar projetos: {error}</div>
    );
  }

  // Lógica de renderização principal (seu código original, agora usando o estado 'projetos')
  if (user.tipo_usuario === "professor") {
    return (
      <main className="p-6">
        <h1 className="text-2xl font-bold">Painel do Professor</h1>
        <p className="mt-2">Bem-vindo(a), {user.nome}!</p>
        <Link to="/projetos/novo">
          <button className="mt-4 px-4 py-2 bg-red-800 text-white rounded hover:bg-red-700">
            + Cadastrar Novo Projeto
          </button>
        </Link>

        <h2 className="text-xl font-semibold mt-8 mb-4">Seus Projetos</h2>

        {/* Renderização condicional se não houver projetos */}
        {projetos.length === 0 ? (
          <p>Você ainda não cadastrou nenhum projeto.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {/* O map agora usa a variável de estado 'projetos' */}
            {projetos.map((proj) => (
              <Link to={`/dashboard/viewproject/${proj.id}`} key={proj.id}>
                <div className="border p-4 rounded-lg shadow bg-gray-100 w-full h-48 hover:shadow-lg hover:border-red-500 transition-all duration-200 cursor-pointer">
                  <h3 className="text-lg font-semibold">{proj.titulo}</h3>
                  <p className="text-sm text-gray-600">
                    Carga horária: {proj.carga_horaria}
                  </p>
                  <p className="text-sm text-gray-600">
                    Duração: {proj.duracao}
                  </p>
                  <p className="text-sm text-gray-600">
                    Tipo: {proj.tipo_projeto}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    );
  } else {
    // Painel do Aluno (também usa os projetos buscados)
    return (
      <main className="p-6">
        <h1 className="text-2xl font-bold">Painel do Aluno</h1>
        <p className="mt-2">Bem-vindo(a), {user.nome}!</p>
        <h2 className="text-xl font-semibold mt-8 mb-4">
          Meus Projetos Inscritos
        </h2>

        {projetos.length === 0 ? (
          <p>Você ainda não se inscreveu em nenhum projeto.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {projetos.map((proj) => (
              <Link
                to={`/dashboard/viewprojectstudent/${proj.id}`}
                key={proj.id}
              >
                <div className="border p-4 rounded-lg shadow bg-gray-100 w-full h-48 hover:shadow-lg hover:border-red-500 transition-all duration-200 cursor-pointer">
                  <h3 className="text-lg font-semibold">{proj.titulo}</h3>
                  <p className="text-sm text-gray-600">
                    Carga horária: {proj.carga_horaria}
                  </p>
                  <p className="text-sm text-gray-600">
                    Duração: {proj.duracao}
                  </p>
                  <p className="text-sm text-gray-600">
                    Tipo: {proj.tipo_projeto}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
        {/* Este botão pode ser removido ou levar a uma página com mais filtros,
            já que todos os projetos já são mostrados aqui. */}
      </main>
    );
  }
}
