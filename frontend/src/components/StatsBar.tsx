"use client";
import type { TranscriptionResult } from "@/lib/api";
import { Clock, DollarSign, Mic, Users } from "lucide-react";

interface Props {
  result: TranscriptionResult;
}

function formatDuration(secs: number) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

const ENGINE_LABEL: Record<string, string> = {
  ibm: "IBM Watson STT",
  elevenlabs: "ElevenLabs Scribe",
};

export default function StatsBar({ result }: Props) {
  const speakerCount = new Set(result.segments.map((s) => s.speaker)).size;

  const stats = [
    {
      icon: <Mic className="w-4 h-4 text-brand" />,
      label: "引擎",
      value: ENGINE_LABEL[result.engine] ?? result.engine,
    },
    {
      icon: <Clock className="w-4 h-4 text-brand" />,
      label: "錄音時長",
      value: formatDuration(result.duration_seconds),
    },
    {
      icon: <Clock className="w-4 h-4 text-brand" />,
      label: "處理耗時",
      value: formatDuration(result.processing_time_seconds),
    },
    {
      icon: <Users className="w-4 h-4 text-brand" />,
      label: "說話人數",
      value: `${speakerCount} 人`,
    },
    {
      icon: <DollarSign className="w-4 h-4 text-brand" />,
      label: "預估費用",
      value: `$${result.estimated_cost_usd.toFixed(4)} USD`,
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
      {stats.map((s) => (
        <div
          key={s.label}
          className="bg-white rounded-lg border border-[#e5e7eb] px-3 py-2.5 flex flex-col gap-1"
        >
          <div className="flex items-center gap-1 text-xs text-[#57606a]">
            {s.icon}
            {s.label}
          </div>
          <p className="text-sm font-semibold text-[#1f2328]">{s.value}</p>
        </div>
      ))}
    </div>
  );
}
