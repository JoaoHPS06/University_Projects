interface SearchBarProps {
  onTextoChange: (texto: string) => void;
  onTipoSelect: (tipo: string | null) => void;
}

export default function SearchBar({
  onTextoChange,
  onTipoSelect,
}: SearchBarProps) {
  return (
    <div className="flex items-center gap-2 bg-white rounded-2xl">
      <input
        type="text"
        placeholder="Pesquisar por título ou professor"
        className="border px-6 py-2 rounded w-72"
        onChange={(e) => onTextoChange(e.target.value)}
      />

      <button
        onClick={() => onTipoSelect("iniciacao")}
        className="px-3 py-1 border rounded-full bg-red-800 text-white hover:text-white"
      >
        Iniciação Científica
      </button>
      <button
        onClick={() => onTipoSelect("monitoria")}
        className="px-3 py-1 border rounded-full bg-red-800 text-white"
      >
        Monitoria
      </button>
      <button
        onClick={() => onTipoSelect("tutoria")}
        className="px-3 py-1 border rounded-full bg-red-800 text-white"
      >
        Tutoria
      </button>
      <button
        onClick={() => onTipoSelect("extensao")}
        className="px-3 py-1 border rounded-full bg-red-800 text-white"
      >
        Projeto de Extensão
      </button>
      <button
        onClick={() => onTipoSelect(null)}
        className="px-3 py-1 border rounded-full text-red-800 border-red-800"
      >
        Limpar Filtros
      </button>
    </div>
  );
}
