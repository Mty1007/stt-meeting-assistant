export type STTEngine = "ibm" | "elevenlabs";
export type SummaryLanguage = "cantonese" | "mandarin" | "english";

export interface SpeakerSegment {
  speaker: string;
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionResult {
  job_id: string;
  engine: STTEngine;
  segments: SpeakerSegment[];
  full_transcript: string;
  duration_seconds: number;
  processing_time_seconds: number;
  estimated_cost_usd: number;
}

export interface MeetingMinutes {
  language: SummaryLanguage;
  summary: string;
  key_points: string[];
  decisions: string[];
  action_items: { owner: string; task: string; due_date: string | null }[];
  raw_output: string;
}

const BASE = "/api";

export async function uploadAudio(file: File): Promise<{ job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Upload failed");
  return res.json();
}

export async function transcribeAudio(
  job_id: string,
  engine: STTEngine
): Promise<TranscriptionResult> {
  const res = await fetch(`${BASE}/transcribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id, engine }),
  });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Transcription failed");
  return res.json();
}

export async function summarize(
  job_id: string,
  transcript: string,
  language: SummaryLanguage
): Promise<MeetingMinutes> {
  const res = await fetch(`${BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id, transcript, language }),
  });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Summarization failed");
  return res.json();
}
