import React from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { Projeto } from "../types";

export default function Newproject() {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<Projeto>({ mode: "onChange" });

  const navigate = useNavigate();

  const onSubmit = (data: Projeto) => {
    fetch("http://localhost:8000/api/projetos/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        titulo: data.titulo,
        carga_horaria: data.cargaHoraria,
        duracao: data.duracao,
        professor: data.professor,
        financiador: data.financiador,
        vagas_voluntarias: data.VagasVoluntarias,
        vagas_remuneradas: data.VagasRemuneradas,
        tipo_projeto: data.tipoProjeto,
        descricao: data.descricao,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Erro ao salvar projeto");
        }
        return response.json();
      })
      .then(() => {
        alert("Projeto salvo com sucesso!");
        navigate("/");
      })
      .catch((err) => {
        console.error("Erro ao salvar projeto", err);
        alert("Erro ao salvar projeto");
      });
  };

  return (
    <main className="mt-16 flex justify-center bg-white min-h-screen">
      <div className="p-6 w-full max-w-5xl">
        <h1 className="text-2xl font-bold mb-6 text-center">
          Cadastrar projeto
        </h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block font-medium mb-1">
                Título do Projeto
              </label>
              <input
                {...register("titulo", { required: true })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Informe o título"
              />
              {errors.titulo && (
                <p className="text-red-500 text-sm">Campo obrigatório</p>
              )}
            </div>

            <div>
              <label className="block font-medium mb-1">Carga Horária</label>
              <input
                {...register("cargaHoraria", { required: true })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Ex: 20h semanais"
              />
              {errors.cargaHoraria && (
                <p className="text-red-500 text-sm">Campo obrigatório</p>
              )}
            </div>

            <div>
              <label className="block font-medium mb-1">Duração</label>
              <input
                {...register("duracao", { required: true })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Informe a duração"
              />
              {errors.duracao && (
                <p className="text-red-500 text-sm">Campo obrigatório</p>
              )}
            </div>

            <div>
              <label className="block font-medium mb-1">
                Professor Orientador
              </label>
              <input
                {...register("professor", { required: true })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Informe o nome do professor"
              />
              {errors.professor && (
                <p className="text-red-500 text-sm">Campo obrigatório</p>
              )}
            </div>

            <div>
              <label className="block font-medium mb-1">
                Quantidade de Vagas Voluntárias
              </label>
              <input
                type="number"
                {...register("VagasVoluntarias", { required: true, min: 1 })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Ex: 2"
              />
              {errors.VagasVoluntarias && (
                <p className="text-red-500 text-sm">Informe no mínimo 1 vaga</p>
              )}
            </div>

            <div>
              <label className="block font-medium mb-1">
                Quantidade de Vagas Remuneradas
              </label>
              <input
                type="number"
                {...register("VagasRemuneradas", { required: true, min: 1 })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Ex: 2"
              />
              {errors.VagasRemuneradas && (
                <p className="text-red-500 text-sm">Informe no mínimo 1 vaga</p>
              )}
            </div>

            <div>
              <label className="block font-medium mb-1">Financiador</label>
              <input
                {...register("financiador", { required: true })}
                className="w-full h-10 border px-2 rounded"
                placeholder="Informe o financiador"
              />
            </div>

            <div>
              <label className="block font-medium mb-1">Tipo de Projeto</label>
              <select
                {...register("tipoProjeto", { required: true })}
                className="w-full h-10 border px-2 rounded"
                defaultValue=""
              >
                <option value="" disabled>
                  Selecione uma categoria
                </option>
                <option value="monitoria">Monitoria</option>
                <option value="tutoria">Tutoria</option>
                <option value="extensao">Projeto de Extensão</option>
                <option value="iniciacao">Iniciação Científica</option>
              </select>
              {errors.tipoProjeto && (
                <p className="text-red-500 text-sm">Selecione uma categoria</p>
              )}
            </div>
          </div>

          <div>
            <label className="block font-medium mb-1">Descrição</label>
            <textarea
              {...register("descricao", { required: true })}
              className="w-full h-40 border px-2 py-2 rounded resize-none"
              placeholder="Descreva o projeto"
            />
            {errors.descricao && (
              <p className="text-red-500 text-sm">Campo obrigatório</p>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={!isValid}
              className="px-6 py-2 bg-gray-300 text-black rounded disabled:opacity-50  hover:text-red-500"
            >
              Cadastrar Projeto
            </button>
            <button
              className="text-red-700 hover:text-red-500"
              onClick={() => navigate("/dashboard")}
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
