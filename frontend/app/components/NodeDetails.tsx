"use client";

interface NodeDetailsProps {
  node: {
    label: string;
    type: string;
    color: string;
    properties: Record<string, any>;
  } | null;
}

export default function NodeDetails({ node }: NodeDetailsProps) {
  if (!node) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-6">
        <div className="text-center text-stone-500">
          <svg
            className="w-12 h-12 mx-auto mb-3 text-stone-300"
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
          <p className="text-sm font-medium">No node selected</p>
          <p className="text-xs mt-1">Click on a node in the graph to view details</p>
        </div>
      </div>
    );
  }

  // Filter out empty or null properties
  const displayProperties = Object.entries(node.properties)
    .filter(([_, value]) => value !== null && value !== undefined && value !== "")
    .slice(0, 15); // Limit to 15 properties for display

  return (
    <div className="bg-white rounded-lg shadow-sm border border-stone-200 overflow-hidden">
      {/* Header */}
      <div
        className="px-4 py-3 border-b border-stone-200"
        style={{ backgroundColor: `${node.color}15` }}
      >
        <div className="flex items-center space-x-2 mb-1">
          <div
            className="w-3 h-3 rounded-full border border-stone-300"
            style={{ backgroundColor: node.color }}
          />
          <span className="text-xs font-semibold text-stone-700 uppercase tracking-wide">
            {node.type}
          </span>
        </div>
        <h3 className="text-base font-bold text-stone-950 break-words">
          {node.label}
        </h3>
      </div>

      {/* Properties */}
      <div className="px-4 py-3">
        <h4 className="text-xs font-semibold text-stone-700 uppercase tracking-wide mb-3">
          Properties
        </h4>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {displayProperties.length > 0 ? (
            displayProperties.map(([key, value]) => (
              <div key={key} className="text-sm">
                <dt className="font-medium text-stone-700 mb-0.5">{key}</dt>
                <dd className="text-stone-600 break-words bg-stone-50 rounded px-2 py-1">
                  {typeof value === "object" ? JSON.stringify(value) : String(value)}
                </dd>
              </div>
            ))
          ) : (
            <p className="text-xs text-stone-500 italic">No properties available</p>
          )}
        </div>
      </div>

      {/* Footer hint */}
      <div className="px-4 py-2 bg-stone-50 border-t border-stone-200">
        <p className="text-xs text-stone-500 text-center">
          Click another node to update details
        </p>
      </div>
    </div>
  );
}

