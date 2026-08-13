"use client";
import { useRef, useState, DragEvent } from "react";
import { UploadCloud } from "lucide-react";
import clsx from "clsx";

interface Props {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

const ACCEPTED = ".mp3,.mp4,.wav,.m4a,.ogg,.flac,.webm";

export default function AudioUploader({ onFileSelected, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file: File | undefined) => {
    if (file) onFileSelected(file);
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div
      className={clsx(
        "border-2 border-dashed rounded-xl p-10 flex flex-col items-center gap-3 cursor-pointer transition-colors select-none",
        dragging
          ? "border-brand bg-blue-50"
          : "border-[#e5e7eb] bg-white hover:border-brand hover:bg-blue-50",
        disabled && "opacity-50 pointer-events-none"
      )}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
    >
      <UploadCloud className="text-brand w-10 h-10" />
      <p className="text-sm font-medium text-[#1f2328]">
        拖拽音頻文件到此，或點擊選擇
      </p>
      <p className="text-xs text-[#57606a]">支持 MP3, MP4, WAV, M4A, OGG, FLAC, WebM</p>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
    </div>
  );
}
