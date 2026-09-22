import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ceramic Glaze Lab · Araştırma Laboratuvarı",
  description:
    "Kaynakları görünür, sınırları açık seramik kimyası araştırma prototipi.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
