import { useNavigate } from "react-router-dom";
import logo from "../assets/logo2.jpeg";
import { useAuth } from "../contexts/AuthContext";

export default function Sidebar() {
  const navigate = useNavigate();
  const { isLogged, logout } = useAuth();
  const { user } = useAuth();

  return (
    <aside className="w-52 text-white bg-red-800 h-screen flex flex-col justify-between shadow-lg">
      <div>
        {/* LOGO */}
        <div className="flex justify-center items-center py-0">
          <img
            src={logo}
            alt="Logo"
            className="w-52 h-52 object-contain mt-0"
          />
        </div>

        {/* Menu */}
        <ul className="space-y-8 mt-8">
          <li
            className="group text-white text-center cursor-pointer py-2 hover:bg-red-700"
            onClick={() => navigate("/")}
          >
            Home
          </li>
          <li
            className="group text-white text-center cursor-pointer py-2 hover:bg-red-700"
            onClick={() => navigate("/projetos-disponiveis")}
          >
            Projetos Disponíveis
          </li>
          {user?.tipo_usuario === "professor" && (
            <li
              className="group text-white text-center cursor-pointer py-2 hover:bg-red-700"
              onClick={() => navigate("/dashboard")}
            >
              Meus Projetos
            </li>
          )}
          {user?.tipo_usuario === "aluno" && (
            <li
              className="group text-white text-center cursor-pointer py-2 hover:bg-red-700"
              onClick={() => navigate("/dashboard")}
            >
              Meus Projetos
            </li>
          )}
        </ul>
      </div>

      {/* Botão Login / Logout */}
      <div className="p-4">
        {!isLogged ? (
          <button
            className="w-full py-2 bg-white text-red-800 font-bold rounded hover:bg-red-100"
            onClick={() => navigate("/login")}
          >
            Fazer login
          </button>
        ) : (
          <button
            className="w-full py-2 bg-red-900 text-white font-bold rounded hover:bg-red-700"
            onClick={logout}
          >
            Logout
          </button>
        )}
      </div>
    </aside>
  );
}
