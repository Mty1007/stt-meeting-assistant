"use client";
import { useState } from "react";
import { CheckCircle, Zap, Users, ClipboardList } from "lucide-react";
import clsx from "clsx";
import type { MeetingMinutes, SummaryLanguage, TranscriptionResult } from "@/lib/api";
import { summarize } from "@/lib/api";

const LANG_OPTIONS: { value: SummaryLanguage; label: string }[] = [
  { value: "cantonese", label: "粵語" },
  { value: "mandarin", label: "普通話" },
  { value: "english", label: "English" },
];

interface Props {
  result: TranscriptionResult;
}

export default function SummaryPanel({ result }: Props) {
  const [language, setLanguage] = useState<SummaryLanguage>("cantonese");
  const [minutes, setMinutes] = useState<MeetingMinutes | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (lang: SummaryLanguage) => {
    setLanguage(lang);
    setLoading(true);
    setError(null);
    try {
      const data = await summarize(result.job_id, result.full_transcript, lang);
      setMinutes(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "生成失敗，請重試");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#e5e7eb] overflow-hidden">
      {/* Language switcher header */}
      <div className="flex items-center justify-between p-4 border-b border-[#e5e7eb]">
        <h2 className="font-semibold text-[#1f2328]">會議紀要</h2>
        <div className="flex gap-1 bg-[#f7f8fa] rounded-lg p-1">
          {LANG_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleGenerate(opt.value)}
              disabled={loading}
              className={clsx(
                "px-3 py-1 rounded-md text-sm font-medium transition-colors",
                language === opt.value && minutes
                  ? "bg-white shadow text-brand border border-[#e5e7eb]"
                  : "text-[#57606a] hover:text-[#1f2328]",
                loading && "opacity-50 cursor-not-allowed"
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="p-5">
        {/* Initial state */}
        {!minutes && !loading && !error && (
          <div className="text-center py-8 text-[#57606a] text-sm">
            <ClipboardList className="w-8 h-8 mx-auto mb-2 opacity-40" />
            選擇語言，點擊生成會議紀要
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-8 text-[#57606a] text-sm animate-pulse">
            watsonx.ai 正在生成紀要...
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Minutes content */}
        {minutes && !loading && (
          <div className="space-y-5">
            {/* Summary */}
            <section>
              <h3 className="text-xs font-semibold text-[#57606a] uppercase tracking-wide mb-2 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5" /> 會議摘要
              </h3>
              <p className="text-sm text-[#1f2328] leading-relaxed bg-[#f7f8fa] rounded-lg p-3">
                {minutes.summary}
              </p>
            </section>

            {/* Key points */}
            {minutes.key_points.length > 0 && (
              <section>
                <h3 className="text-xs font-semibold text-[#57606a] uppercase tracking-wide mb-2 flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5" /> 主要討論點
                </h3>
                <ul className="space-y-1.5">
                  {minutes.key_points.map((pt, i) => (
                    <li key={i} className="flex gap-2 text-sm text-[#1f2328]">
                      <span className="text-brand font-bold mt-0.5">·</span>
                      {pt}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Decisions */}
            {minutes.decisions.length > 0 && (
              <section>
                <h3 className="text-xs font-semibold text-[#57606a] uppercase tracking-wide mb-2 flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5" /> 決策結論
                </h3>
                <ul className="space-y-1.5">
                  {minutes.decisions.map((d, i) => (
                    <li key={i} className="flex gap-2 text-sm text-[#1f2328]">
                      <span className="text-green-600 font-bold mt-0.5">✓</span>
                      {d}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Action items */}
            {minutes.action_items.length > 0 && (
              <section>
                <h3 className="text-xs font-semibold text-[#57606a] uppercase tracking-wide mb-2 flex items-center gap-1">
                  <Users className="w-3.5 h-3.5" /> Action Items
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="bg-[#f7f8fa] text-[#57606a] text-left text-xs">
                        <th className="px-3 py-2 border border-[#e5e7eb] rounded-tl">負責人</th>
                        <th className="px-3 py-2 border border-[#e5e7eb]">事項</th>
                        <th className="px-3 py-2 border border-[#e5e7eb] rounded-tr">截止日期</th>
                      </tr>
                    </thead>
                    <tbody>
                      {minutes.action_items.map((item, i) => (
                        <tr key={i} className="border-b border-[#e5e7eb]">
                          <td className="px-3 py-2 border border-[#e5e7eb] font-medium">{item.owner}</td>
                          <td className="px-3 py-2 border border-[#e5e7eb]">{item.task}</td>
                          <td className="px-3 py-2 border border-[#e5e7eb] text-[#57606a]">
                            {item.due_date ?? "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
