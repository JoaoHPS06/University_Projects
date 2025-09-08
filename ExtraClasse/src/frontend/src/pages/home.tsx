export default function Home() {
  return (
    <div className="p-10 bg-white min-h-screen text-gray-800">
      <h1 className="text-4xl font-bold text-red-800 mb-4">Bem-vindo ao ExtraClasse</h1>

      <p className="text-lg max-w-3xl mb-6">
        O <strong>ExtraClasse</strong> é um sistema desenvolvido para conectar estudantes e professores da UFOP em torno de oportunidades extracurriculares como Iniciação Científica, Monitorias, Tutorias, Projetos de Extensão e Pesquisas Voluntárias.
      </p>

      <p className="text-lg max-w-3xl mb-6">
        Aqui, os professores podem divulgar suas vagas e os alunos podem visualizar e se candidatar às oportunidades que se encaixam em seus interesses e perfis acadêmicos.
      </p>

      <div className="flex gap-4 mt-8">
        <button
          onClick={() => window.location.href = "/projetos-disponiveis"}
          className="px-6 py-3 bg-red-800 text-white rounded hover:bg-red-700 transition"
        >
          Ver Projetos Disponíveis
        </button>

        <button
          onClick={() => window.location.href = "/login"}
          className="px-6 py-3 border border-red-800 text-red-800 rounded hover:bg-red-100 transition"
        >
          Cadastrar Vaga (Professor)
        </button>
      </div>
    </div>
  );
}
