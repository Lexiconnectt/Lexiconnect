"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import SearchBar from "./components/SearchBar";
import DatabaseStatistics from "./components/DatabaseStatistics";

// Dynamically import the graph component to avoid SSR issues with Sigma.js
const GraphVisualization = dynamic(
  () => import("./components/GraphVisualization"),
  { ssr: false }
);

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [visualizeWord, setVisualizeWord] = useState<string | undefined>(undefined);

  useEffect(() => {
    setMounted(true);
  }, []);
  
  const handleVisualizeWord = (word: string) => {
    setVisualizeWord(word);
  };
  
  const handleClearVisualization = () => {
    setVisualizeWord(undefined);
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-950 mb-1.5">
            Linguistic Network Visualization
          </h1>
          <p className="text-sm text-stone-600">
            Search morphemes and words, then explore their connections in the graph.
          </p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-[2fr,1fr] gap-6 mb-6">
          {/* Left Column: Search and Graph */}
          <div className="space-y-4">
            {/* Search Toolbar */}
            <SearchBar onVisualizeWord={handleVisualizeWord} />

            {/* Graph Card */}
            <div className="bg-white rounded-lg shadow-sm border border-stone-200 overflow-hidden">
              {/* Word visualization header */}
              {visualizeWord && (
                <div className="px-4 py-2 bg-blue-50 border-b border-blue-200 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg
                      className="w-4 h-4 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span className="text-sm font-medium text-blue-900">
                      Visualizing morphology for: <span className="font-bold">{visualizeWord}</span>
                    </span>
                  </div>
                  <button
                    onClick={handleClearVisualization}
                    className="text-xs px-2 py-1 text-blue-700 hover:text-blue-900 hover:bg-blue-100 rounded transition-colors"
                  >
                    Clear
                  </button>
                </div>
              )}
              
              <div className="relative w-full bg-stone-50" style={{ height: "calc(100vh - 280px)", minHeight: "500px" }}>
                {mounted ? (
                  <GraphVisualization searchWord={visualizeWord} />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-stone-700 rounded-full animate-bounce"></div>
                      <div
                        className="w-4 h-4 bg-stone-700 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-4 h-4 bg-stone-700 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
              {/* Interaction hint footer */}
              <div className="px-4 py-2 border-t border-stone-200 bg-white">
                <div className="flex items-center justify-center">
                  <span className="text-xs text-stone-500">
                    Drag to pan • Scroll to zoom • Click nodes to interact
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Database Statistics */}
          <div className="lg:sticky lg:top-6 h-fit">
            <DatabaseStatistics />
          </div>
        </div>
      </div>
    </div>
  );
}
