import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar"; // Verifique se o caminho está correto

export default function ProtectedLayout() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 p-4 overflow-auto bg-white">
        {/* As rotas aninhadas serão renderizadas aqui 👇 */}
        <Outlet />
      </main>
    </div>
  );
}