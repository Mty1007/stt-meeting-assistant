"use client";
import { useState } from "react";
import { Mic2 } from "lucide-react";
import AudioUploader from "@/components/AudioUploader";
import EngineSelector from "@/components/EngineSelector";
import TranscriptView from "@/components/TranscriptView";
import SummaryPanel from "@/components/SummaryPanel";
import StatsBar from "@/components/StatsBar";
import { uploadAudio, transcribeAudio } from "@/lib/api";
import type { STTEngine, TranscriptionResult } from "@/lib/api";

type Step = "idle" | "uploading" | "transcribing" | "done" | "error";

export default function HomePage() {
  const [engine, setEngine] = useState<STTEngine>("ibm");
  const [step, setStep] = useState<Step>("idle");
  const [statusMsg, setStatusMsg] = useState("");
  const [result, setResult] = useState<TranscriptionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setResult(null);

    try {
      // Step 1: Upload
      setStep("uploading");
      setStatusMsg(`正在上傳 ${file.name}…`);
      const { job_id } = await uploadAudio(file);

      // Step 2: Transcribe
      setStep("transcribing");
      setStatusMsg("正在進行說話人分離與語音識別…（可能需要數分鐘）");
      const transcription = await transcribeAudio(job_id, engine);

      setResult(transcription);
      setStep("done");
      setStatusMsg("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "發生未知錯誤");
      setStep("error");
    }
  };

  const isProcessing = step === "uploading" || step === "transcribing";

  return (
    <main className="min-h-screen py-10 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex items-center gap-3">
          <div className="bg-brand rounded-xl p-2.5">
            <Mic2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#1f2328]">STT 會議助手</h1>
            <p className="text-sm text-[#57606a]">粵英混語語音識別 · 智能會議紀要</p>
          </div>
        </header>

        {/* Upload & Engine */}
        <div className="bg-white rounded-xl border border-[#e5e7eb] p-5 space-y-4">
          <div>
            <p className="text-sm font-medium text-[#1f2328] mb-2">選擇 STT 引擎</p>
            <EngineSelector value={engine} onChange={setEngine} disabled={isProcessing} />
          </div>
          <div>
            <p className="text-sm font-medium text-[#1f2328] mb-2">上傳會議錄音</p>
            <AudioUploader onFileSelected={handleFile} disabled={isProcessing} />
          </div>
        </div>

        {/* Processing indicator */}
        {isProcessing && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-4 h-4 rounded-full border-2 border-brand border-t-transparent animate-spin" />
            <p className="text-sm text-brand font-medium">{statusMsg}</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
            <strong>錯誤：</strong> {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <>
            {/* Stats */}
            <StatsBar result={result} />

            {/* Transcript */}
            <div className="bg-white rounded-xl border border-[#e5e7eb] p-5">
              <h2 className="font-semibold text-[#1f2328] mb-4">逐字稿</h2>
              <TranscriptView segments={result.segments} />
            </div>

            {/* Summary */}
            <SummaryPanel result={result} />
          </>
        )}
      </div>
    </main>
  );
}
