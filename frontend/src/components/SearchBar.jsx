import { useEffect, useRef, useState } from "react";
import { searchCompanies } from "../api.js";

export default function SearchBar({ onSelect }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const { results } = await searchCompanies(query);
        setSuggestions(results || []);
        setOpen(true);
        setActiveIndex(-1);
      } catch {
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function pick(item) {
    setQuery(item.name);
    setOpen(false);
    onSelect(item.symbol);
  }

  function handleKeyDown(e) {
    if (!open || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIndex >= 0) {
      e.preventDefault();
      pick(suggestions[activeIndex]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div className="relative max-w-xl" ref={containerRef}>
      <label htmlFor="company-search" className="sr-only">
        Search for a company
      </label>
      <div className="flex items-center bg-white rounded-xl shadow-card px-4 py-3 focus-within:ring-2 focus-within:ring-coral">
        <svg
          aria-hidden="true"
          className="w-5 h-5 text-teal mr-3 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"
          />
        </svg>
        <input
          id="company-search"
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls="search-suggestions"
          aria-autocomplete="list"
          className="w-full outline-none text-slate-800 placeholder:text-slate-400"
          placeholder="Search by company name or symbol (e.g. TCS, Infosys, Reliance)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
          onKeyDown={handleKeyDown}
        />
        {loading && (
          <span className="ml-2 text-xs text-slate-400 animate-pulse">…</span>
        )}
      </div>

      {open && suggestions.length > 0 && (
        <ul
          id="search-suggestions"
          role="listbox"
          className="absolute z-20 mt-2 w-full bg-white rounded-xl shadow-card overflow-hidden divide-y divide-sand"
        >
          {suggestions.map((item, idx) => (
            <li key={item.symbol || item.url} role="option" aria-selected={idx === activeIndex}>
              <button
                type="button"
                onClick={() => pick(item)}
                className={`w-full text-left px-4 py-3 hover:bg-sand transition-colors focus-ring ${
                  idx === activeIndex ? "bg-sand" : ""
                }`}
              >
                <span className="font-medium text-slate-800">{item.name}</span>
                {item.symbol && (
                  <span className="ml-2 text-xs text-teal font-semibold">
                    {item.symbol}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
