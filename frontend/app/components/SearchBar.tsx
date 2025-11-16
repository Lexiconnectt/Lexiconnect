"use client";

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ConcordanceResult {
  target: string;
  left_context: string[];
  right_context: string[];
  phrase_id: string;
  text_title: string;
  segnum: string;
  word_index: number | null;
  glosses?: string[] | null;
}

interface SearchBarProps {
  onSearchResults?: (results: ConcordanceResult[]) => void;
  onVisualizeWord?: (word: string) => void;
}

export default function SearchBar({ onSearchResults, onVisualizeWord }: SearchBarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState<"morpheme" | "word">("morpheme");
  const [results, setResults] = useState<ConcordanceResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setResults([]);
      setShowResults(false);
      onSearchResults?.([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/linguistic/concordance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          target: searchQuery.trim(),
          target_type: searchType,
          context_size: 3,
          limit: 100,
        }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      setResults(data);
      setShowResults(true);
      onSearchResults?.(data);
    } catch (error) {
      console.error("Error searching:", error);
      setResults([]);
      setShowResults(false);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const placeholder =
    searchType === "morpheme"
      ? 'Search morphemes (e.g. "ke-")'
      : 'Search words (e.g. "run")';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-3">
      {/* Compact Search Toolbar */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Search Input */}
        <div className="flex-1 min-w-[200px] relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className="w-full px-3 py-2 pl-9 text-sm bg-white border border-stone-300 rounded-md text-stone-950 focus:outline-none focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
          />
          <svg
            className="absolute left-2.5 top-2.5 w-4 h-4 text-stone-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        {/* Segmented Control */}
        <div className="flex items-center bg-stone-100 rounded-md p-1 border border-stone-200">
          <button
            type="button"
            onClick={() => setSearchType("morpheme")}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-all ${
              searchType === "morpheme"
                ? "bg-stone-600 text-white shadow-sm"
                : "text-stone-700 hover:text-stone-900"
            }`}
            title="Search for morphemes"
          >
            Morpheme
          </button>
          <button
            type="button"
            onClick={() => setSearchType("word")}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-all ${
              searchType === "word"
                ? "bg-stone-600 text-white shadow-sm"
                : "text-stone-700 hover:text-stone-900"
            }`}
            title="Search for words"
          >
            Word
          </button>
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="px-4 py-2 text-sm font-medium text-white bg-stone-600 hover:bg-stone-700 rounded-md transition-colors disabled:bg-stone-400 disabled:cursor-not-allowed flex items-center space-x-2 min-w-[90px] justify-center"
        >
          {isSearching ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Searching...</span>
            </>
          ) : (
            <span>Search</span>
          )}
        </button>
      </div>

      {/* Search Results */}
      {showResults && (
        <div className="mt-3 pt-3 border-t border-stone-200 max-h-[400px] overflow-y-auto">
          {results.length === 0 ? (
            <div className="p-4 text-center text-sm text-stone-500">
              No results found
            </div>
          ) : (
            <div>
              <div className="text-xs font-semibold text-stone-700 mb-2 px-1">
                Found {results.length} result{results.length !== 1 ? "s" : ""}
              </div>
              {results.map((result, index) => (
                <div
                  key={`${result.phrase_id}-${result.word_index}-${index}`}
                  className="mb-2 p-3 bg-stone-50 rounded-md border border-stone-200 hover:bg-stone-100 transition-colors"
                >
                  {/* Context Line */}
                  <div className="text-sm mb-1">
                    <span className="text-stone-500">
                      {result.left_context.join(" ")}
                    </span>
                    <span className="font-semibold text-stone-900 mx-1">
                      {result.target}
                    </span>
                    <span className="text-stone-500">
                      {result.right_context.join(" ")}
                    </span>
                  </div>

                  {/* Glosses */}
                  {result.glosses && result.glosses.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {result.glosses.map((gloss, idx) => (
                        <span
                          key={idx}
                          className="inline-block px-2 py-0.5 text-xs bg-stone-100 text-stone-700 rounded"
                        >
                          {gloss}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Metadata and Actions */}
                  <div className="flex items-center justify-between mt-2">
                    <div className="text-xs text-stone-500 flex items-center space-x-2">
                      <span>{result.text_title || "Untitled"}</span>
                      {result.segnum && <span>• Section {result.segnum}</span>}
                      {result.word_index !== null && (
                        <span>• Word {result.word_index + 1}</span>
                      )}
                    </div>
                    
                    {/* Visualize button for word search results */}
                    {searchType === "word" && onVisualizeWord && (
                      <button
                        onClick={() => onVisualizeWord(result.target)}
                        className="text-xs px-2 py-1 bg-stone-600 hover:bg-stone-700 text-white rounded transition-colors flex items-center space-x-1"
                        title="Visualize word morphology"
                      >
                        <svg
                          className="w-3 h-3"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                          />
                        </svg>
                        <span>Visualize</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
