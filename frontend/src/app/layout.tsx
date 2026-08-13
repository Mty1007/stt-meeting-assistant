import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "STT Meeting Assistant",
  description: "Cantonese-English meeting transcription & minutes",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#f7f8fa] text-[#1f2328] min-h-screen font-sans">
        {children}
      </body>
    </html>
  );
}
