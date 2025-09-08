import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo2.jpeg";
import { useAuth } from "../contexts/AuthContext";

interface loginfields {
  matricula: string;
  senha: string;
}

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { register, handleSubmit } = useForm<loginfields>();

  async function submit(data: loginfields) {
    if (!data.matricula || !data.senha) return;

    let mockUserData;

    // Diferencia professor e aluno por matrícula
    if (data.matricula === "2314129" && data.senha === "1234") {
      mockUserData = {
        id: 1,
        matricula: data.matricula,
        nome: "Guilherme",
        tipo_usuario: "professor" as const,
      };
    } else if (data.matricula === "2314131" && data.senha === "1234") {
      mockUserData = {
        id: 2,
        matricula: data.matricula,
        nome: "Gustavo",
        tipo_usuario: "aluno" as const,
      };
    } else {
      alert("Usuário não encontrado");
      return;
    }

    // Passa o mock para o contexto de autenticação
    login(mockUserData);

    // Redireciona para o dashboard
    navigate("/dashboard");
  }

  return (
    <main className="mt-16 flex justify-center bg-white min-h-screen">
      <form
        className="w-80 flex flex-col gap-4"
        onSubmit={handleSubmit(submit)}
      >
        <div className="flex justify-center items-center">
          <img
            src={logo}
            alt="icon"
            className="w-72 h-72 bg-black"
            onClick={() => navigate("/")}
          />
        </div>
        <label className="font-bold">Matricula:</label>
        <input
          {...register("matricula")}
          className="h-12 w-full border bg-gray-100 rounded-md p-4 shadow-sm"
          placeholder="Insira a matrícula"
        />
        <label className="font-bold">Senha:</label>
        <input
          {...register("senha")}
          className="h-12 w-full border bg-gray-100 rounded-md p-4 shadow-sm"
          placeholder="Digite a senha"
          type="password"
        />
        <div>
          <button className="mt-4 h-12 rounded-md bg-red-800 text-white w-full text-center">
            Entrar
          </button>
        </div>
      </form>
    </main>
  );
}
