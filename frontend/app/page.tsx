// app/page.tsx
"use client";

import { useState, useRef } from "react";
import { UploadCloud, Terminal, Loader2, Play } from "lucide-react";

interface StreamStep {
  node: string;
  status: string;
  answer?: string;
}

export default function Home() {
  // Upload States
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Chat / Query States
  const [query, setQuery] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamSteps, setStreamSteps] = useState<StreamStep[]>([]);
  const [finalAnswer, setFinalAnswer] = useState<string | null>(null);

  // Handle PDF Ingestion
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus(`Ingesting ${file.name}...`);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus(`✅ Vectorized ${data.chunks_processed} chunks.`);
      } else {
        setUploadStatus("❌ Error: Processing failed.");
      }
    } catch (error) {
      setUploadStatus("❌ Error: Connection failed.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // Handle SSE Streaming Query execution
  const executeQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsStreaming(true);
    setStreamSteps([]);
    setFinalAnswer(null);

    try {
      // Connect to our FastAPI SSE endpoint
      const response = await fetch(`http://localhost:8000/query/stream?question=${encodeURIComponent(query)}`);

      if (!response.body) {
        throw new Error("No readable stream body found.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        // Decode string fragments
        buffer += decoder.decode(value, { stream: true });

        // SSE formatting chunks are separated by double newlines \n\n
        const lines = buffer.split("\n\n");
        // Keep the last incomplete fragment in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.replace("data: ", "").trim();
            try {
              const parsedData: StreamStep = JSON.parse(jsonStr);

              // Append to running list of agent thought steps
              setStreamSteps((prev) => {
                // Prevent duplicate node logs if the graph loops back
                const filtered = prev.filter(step => step.status !== parsedData.status);
                return [...filtered, parsedData];
              });

              // If the current step contains the final answer, capture it
              if (parsedData.answer) {
                setFinalAnswer(parsedData.answer);
              }
            } catch (err) {
              console.error("Error parsing stream block:", err);
            }
          }
        }
      }
    } catch (error) {
      console.error("Streaming error:", error);
      setStreamSteps((prev) => [
        ...prev,
        { node: "error", status: "❌ System Connection Error." },
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-start p-8 md:p-24 relative overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-neon opacity-5 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-15%] right-[-10%] w-[30vw] h-[30vw] bg-neon opacity-[0.03] blur-[100px] rounded-full pointer-events-none" />

      {/* HEADER */}
      <header className="w-full max-w-5xl flex flex-col items-start gap-4 mb-16 z-10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-1 bg-neon" />
          <p className="tracking-[0.3em] text-neon text-sm font-bold uppercase">System Online</p>
          <div className="w-2 h-2 bg-neon rounded-full animate-pulse ml-1" />
        </div>
        <h1 className="font-heading text-6xl md:text-8xl font-bold uppercase tracking-tighter">
          SAGE <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon to-white">ENGINE</span>
        </h1>
        <p className="text-muted max-w-2xl text-lg font-mono leading-relaxed mt-4">
          Agentic Retrieval-Augmented Generation. Upload your documents, and the self-correcting neural loop will extract, evaluate, and synthesize answers in real-time.
        </p>
      </header>

      {/* DASHBOARD BLOCK */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 gap-8 z-10">

        {/* COLUMN 1: Ingestion & System Stats */}
        <div className="md:col-span-4 flex flex-col gap-4">
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileUpload}
          />

          <div
            onClick={() => !isUploading && fileInputRef.current?.click()}
            className={`bg-surface border ${isUploading ? 'border-neon' : 'border-[#333] hover:border-neon hover:shadow-neon'} transition-all duration-300 rounded-none p-8 flex flex-col items-center justify-center cursor-pointer group h-[300px] relative`}
          >
            {isUploading ? (
              <Loader2 className="w-12 h-12 text-neon animate-spin mb-4" />
            ) : (
              <UploadCloud className="w-12 h-12 text-muted group-hover:text-neon group-hover:scale-110 transition-all duration-300 mb-4" />
            )}
            <h3 className="font-heading uppercase text-xl text-center mb-2">
              {isUploading ? "Processing" : "Initialize Data"}
            </h3>
            <p className="text-muted text-sm text-center font-mono">
              {uploadStatus || "Click to browse for PDF"}
            </p>
            <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-neon/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          </div>

          <div className="bg-surface border border-[#333] p-6 rounded-none">
            <h4 className="font-heading uppercase text-sm text-neon mb-4">System Metrics</h4>
            <div className="space-y-3 font-mono text-sm text-muted">
              <div className="flex justify-between"><span>Vector DB:</span> <span className="text-white">Qdrant Active</span></div>
              <div className="flex justify-between"><span>LLM Core:</span> <span className="text-white">Llama 3.2</span></div>
              <div className="flex justify-between"><span>Retrieval:</span> <span className="text-white">Hybrid (RRF)</span></div>
            </div>
          </div>
        </div>

        {/* COLUMN 2: Stream Agent Terminal */}
        <div className="md:col-span-8 bg-surface border border-[#333] rounded-none p-6 flex flex-col min-h-[500px]">
          <div className="flex items-center gap-3 border-b border-[#333] pb-4 mb-4">
            <Terminal className="w-5 h-5 text-neon" />
            <h3 className="font-heading uppercase text-lg tracking-wider">Agent Terminal</h3>
            <span className="ml-auto text-xs font-mono text-muted/60 uppercase tracking-wider">{isStreaming ? 'Running' : 'Ready'}</span>
          </div>

          {/* DYNAMIC LOG WINDOW */}
          <div className="flex-1 overflow-y-auto font-mono text-sm space-y-3 max-h-[340px] mb-4 pr-2">
            {streamSteps.length === 0 && !isStreaming && (
              <div className="text-muted">Awaiting input sequence...</div>
            )}

            {/* Render each node's running execution event */}
            {streamSteps.map((step, index) => (
              <div key={index} className="flex flex-col gap-1 border-l-2 border-[#333] hover:border-l-neon pl-3 py-1.5 transition-colors duration-200 animate-fadeIn">
                <span className="text-xs uppercase text-neon tracking-wider font-bold">[{step.node}]</span>
                <span className="text-gray-300 leading-relaxed">{step.status}</span>
              </div>
            ))}

            {/* Display the synthesized final answer once it lands */}
            {finalAnswer && (
              <div className="mt-6 border border-neon/30 bg-[#121202] p-4 text-white font-mono rounded-none border-l-4 border-l-neon animate-slideUp">
                <div className="font-heading uppercase text-xs text-neon mb-2 tracking-widest">Final Synthesis:</div>
                <p className="leading-relaxed whitespace-pre-line">{finalAnswer}</p>
              </div>
            )}

            {isStreaming && !finalAnswer && (
              <div className="flex items-center gap-2 text-muted italic pt-2">
                <Loader2 className="w-4 h-4 animate-spin text-neon" />
                <span>Computing next node transition...</span>
              </div>
            )}
          </div>

          {/* FORM USER INPUT */}
          <form onSubmit={executeQuery} className="mt-auto flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isStreaming}
              placeholder="Query the knowledge base..."
              className="flex-1 bg-background border border-[#333] focus:border-neon focus:shadow-[0_0_8px_rgba(228,240,26,0.15)] outline-none px-4 py-3 font-mono text-white rounded-none transition-all duration-300 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isStreaming || !query.trim()}
              className="bg-white text-black font-heading font-bold uppercase px-6 py-3 hover:bg-neon transition-colors duration-300 disabled:opacity-40 disabled:bg-white/60 flex items-center gap-2"
            >
              {isStreaming ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-black" />
              )}
              Execute
            </button>
          </form>
        </div>

      </div>
    </main>
  );
}