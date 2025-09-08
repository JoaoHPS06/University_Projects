import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Projeto } from "../types";
import { useNavigate } from "react-router-dom";

export default function ProjetoCadastro() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [projeto, setProjeto] = useState<Projeto | null>(null);

  // Estados para cada campo do formulario
  const [nome, setNome] = useState("");
  const [matricula, setMatricula] = useState("");
  const [email, setEmail] = useState("");
  const [coeficiente, setCoeficiente] = useState("");
  const [curso, setCurso] = useState("");

  useEffect(() => {
    fetch(`http://localhost:8000/api/projetos/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        const adaptado: Projeto = {
          id: data.id,
          titulo: data.titulo,
          cargaHoraria: data.carga_horaria,
          duracao: data.duracao,
          professor: data.professor,
          tipoProjeto: data.tipo_projeto,
          financiador: data.financiador,
          VagasVoluntarias: data.vagas_voluntarias,
          VagasRemuneradas: data.vagas_remuneradas,
          descricao: data.descricao,
        };
        setProjeto(adaptado);
      });
  }, [id]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    fetch(`http://localhost:8000/api/projetos/${id}/inscricao/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, matricula, email, coeficiente, curso }),
    })
      .then((res) => {
        if (res.ok) {
          alert("Inscrição realizada com sucesso!");
          // opcional: limpar campos
          setNome("");
          setMatricula("");
          setEmail("");
          setCoeficiente("");
          setCurso("");
          navigate("/projetos-disponiveis");
        } else {
          alert("Erro ao se inscrever no projeto");
        }
      })
      .catch((err) => console.error(err));
  };

  // Verifica se todos os campos estao preenchidos
  const isValid =
    nome.trim() !== "" &&
    matricula.trim() !== "" &&
    email.trim() !== "" &&
    coeficiente.trim() !== "" &&
    curso.trim() !== "";

  if (!projeto) return <p>Não existem projetos disponíveis no momento</p>;

  return (
    <main className="min-h-screen flex justify-center items-start bg-white pt-20 px-6">
      <div className="w-full max-w-xl">
        <h1 className="text-2xl font-bold mb-4 text-center">
          Inscrever-se em projeto
        </h1>
        <h2 className="text-xl font-semibold mb-2 text-center">
          {projeto.titulo}
        </h2>
        <p className="mb-6 text-center">{projeto.descricao}</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex flex-col space-y-4">
            <div>
              <label className="block font-medium mb-1">Nome</label>
              <input
                type="text"
                className="w-full h-10 border px-3 py-2 rounded"
                placeholder="Informe seu nome"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-1">Matrícula</label>
              <input
                type="text"
                className="w-full h-10 border px-3 py-2 rounded"
                placeholder="Informe sua matrícula"
                value={matricula}
                onChange={(e) => setMatricula(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-1">E-mail</label>
              <input
                type="email"
                className="w-full h-10 border px-3 py-2 rounded"
                placeholder="Informe seu e-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-1">Coeficiente</label>
              <input
                type="tel"
                className="w-full h-10 border px-3 py-2 rounded"
                placeholder="Informe seu coeficiente"
                value={coeficiente}
                onChange={(e) => setCoeficiente(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-1">Curso</label>
              <input
                type="text"
                className="w-full h-10 border px-3 py-2 rounded"
                placeholder="Informe seu curso"
                value={curso}
                onChange={(e) => setCurso(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="flex justify-center">
            <button
              type="submit"
              disabled={!isValid}
              className="px-6 py-2 bg-gray-300 text-black rounded disabled:opacity-50 hover:text-red-500"
            >
              Enviar Cadastro
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
