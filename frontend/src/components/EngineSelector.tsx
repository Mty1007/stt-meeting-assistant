"use client";
import clsx from "clsx";
import type { STTEngine } from "@/lib/api";

interface Props {
  value: STTEngine;
  onChange: (v: STTEngine) => void;
  disabled?: boolean;
}

const OPTIONS: { value: STTEngine; label: string; desc: string }[] = [
  {
    value: "ibm",
    label: "IBM Watson STT",
    desc: "中文廣頻模型 · zh-CN_BroadbandModel",
  },
  {
    value: "elevenlabs",
    label: "ElevenLabs Scribe v1",
    desc: "多語言混合識別 · 原生粵英混語支持",
  },
];

export default function EngineSelector({ value, onChange, disabled }: Props) {
  return (
    <div className="flex gap-3">
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          type="button"
          disabled={disabled}
          onClick={() => onChange(opt.value)}
          className={clsx(
            "flex-1 rounded-lg border p-3 text-left transition-colors",
            value === opt.value
              ? "border-brand bg-blue-50"
              : "border-[#e5e7eb] bg-white hover:border-brand",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          <p className={clsx("text-sm font-semibold", value === opt.value ? "text-brand" : "text-[#1f2328]")}>
            {opt.label}
          </p>
          <p className="text-xs text-[#57606a] mt-0.5">{opt.desc}</p>
        </button>
      ))}
    </div>
  );
}
