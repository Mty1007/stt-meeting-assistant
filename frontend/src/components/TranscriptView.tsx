"use client";
import type { SpeakerSegment } from "@/lib/api";

// Generate a stable color per speaker label
const SPEAKER_COLORS = [
  "bg-blue-100 text-blue-800",
  "bg-purple-100 text-purple-800",
  "bg-green-100 text-green-800",
  "bg-orange-100 text-orange-800",
  "bg-pink-100 text-pink-800",
  "bg-teal-100 text-teal-800",
];

function formatTime(secs: number) {
  const m = Math.floor(secs / 60).toString().padStart(2, "0");
  const s = Math.floor(secs % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

interface Props {
  segments: SpeakerSegment[];
}

export default function TranscriptView({ segments }: Props) {
  // Map speaker label → color index
  const speakerColorMap = new Map<string, string>();
  let colorIdx = 0;
  for (const seg of segments) {
    if (!speakerColorMap.has(seg.speaker)) {
      speakerColorMap.set(
        seg.speaker,
        SPEAKER_COLORS[colorIdx % SPEAKER_COLORS.length]
      );
      colorIdx++;
    }
  }

  return (
    <div className="space-y-3">
      {segments.map((seg, i) => (
        <div key={i} className="flex gap-3 items-start">
          {/* Speaker badge */}
          <div className="flex flex-col items-center gap-1 min-w-[80px]">
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded-full ${speakerColorMap.get(seg.speaker)}`}
            >
              {seg.speaker.replace("SPEAKER_0", "說話人 ")}
            </span>
            <span className="text-[10px] text-[#57606a] whitespace-nowrap">
              {formatTime(seg.start)} – {formatTime(seg.end)}
            </span>
          </div>

          {/* Text bubble */}
          <div className="flex-1 bg-white border border-[#e5e7eb] rounded-lg px-4 py-2 text-sm leading-relaxed text-[#1f2328]">
            {seg.text}
          </div>
        </div>
      ))}
    </div>
  );
}
