import SearchBar from "../components/Searchbar";
import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { Projeto } from "../types";

export default function ProjetoDisponivel() {
  const [paginaAtual, setPaginaAtual] = useState(1);
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const itensPorPagina = 15;

  useEffect(() => {
    fetch("http://localhost:8000/api/projetos/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Erro ao buscar projetos");
        }
        return response.json();
      })
      .then((data) => {
        const adaptado = data.map(
          (item: any): Projeto => ({
            id: item.id,
            titulo: item.titulo,
            cargaHoraria: item.carga_horaria,
            duracao: item.duracao,
            professor: item.professor,
            tipoProjeto: item.tipo_projeto,
            financiador: item.financiador,
            VagasVoluntarias: item.vagas_voluntarias,
            VagasRemuneradas: item.vagas_remuneradas,
            descricao: item.descricao,
          })
        );
        setProjetos(adaptado);
      })
      .catch((err) => console.error("Erro ao carregar projetos", err));
  }, []);
  const [filtroTexto, setFiltroTexto] = useState("");
  const [filtroTipo, setFiltroTipo] = useState<string | null>(null);

  const projetosFiltrados = projetos.filter((proj) => {
    const textoMatch =
      proj.titulo.toLowerCase().startsWith(filtroTexto.toLowerCase()) ||
      proj.professor.toLowerCase().startsWith(filtroTexto.toLowerCase());

    const tipoMatch = filtroTipo ? proj.tipoProjeto === filtroTipo : true;

    return textoMatch && tipoMatch;
  });

  const totalPaginas = Math.ceil(projetosFiltrados.length / itensPorPagina);
  const inicio = (paginaAtual - 1) * itensPorPagina;
  const fim = inicio + itensPorPagina;
  const projetosPaginados = projetosFiltrados.slice(inicio, fim);

  return (
    <main className=" flex-1 p-6 bg-white">
      <h1 className="text-2xl font-bold mb-4">Projetos Disponíveis</h1>
      <SearchBar
        onTextoChange={(texto) => {
          setFiltroTexto(texto);
          setPaginaAtual(1); // Reinicia a paginação
        }}
        onTipoSelect={(tipo) => {
          setFiltroTipo(tipo);
          setPaginaAtual(1); // Reinicia a paginação
        }}
      />

      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-10 ">
        {projetosPaginados.map((proj) => (
          <Link to={`/projeto/${proj.id}`} key={proj.id}>
            <div className="border p-4 rounded-lg shadow bg-gray-100 w-72 h-48 hover:shadow-lg hover:border-red-500 transition-all duration-200 cursor-pointer">
              <h3 className="text-lg font-semibold">{proj.titulo}</h3>
              <p className="text-sm text-gray-600">
                Carga horária: {proj.cargaHoraria}
              </p>
              <p className="text-sm text-gray-600">Duração: {proj.duracao}</p>
              <p className="text-sm text-gray-600">
                Orientador(a): {proj.professor}
              </p>
              <p className="text-sm text-gray-600">Tipo: {proj.tipoProjeto}</p>
            </div>
          </Link>
        ))}
      </div>

      {projetos.length > itensPorPagina && (
        <div className="flex justify-center items-center gap-4 mt-4">
          <button
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50 hover:text-red-500"
            onClick={() => setPaginaAtual((p) => p - 1)}
            disabled={paginaAtual === 1}
          >
            Anterior
          </button>

          <span className="text-gray-600">
            Página {paginaAtual} de {totalPaginas}
          </span>

          <button
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50 hover:text-red-500"
            onClick={() => setPaginaAtual((p) => p + 1)}
            disabled={paginaAtual === totalPaginas}
          >
            Próxima
          </button>
        </div>
      )}
    </main>
  );
}
