import type { Metadata } from "next";
import "./globals.css";
import "./workbench.css";
import "./library.css";
import "./archive.css";
import LabNavigation from '../components/lab-navigation';
import {ExperimentSession} from '../components/experiment-session';

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
      <body><ExperimentSession><LabNavigation />{children}</ExperimentSession></body>
    </html>
  );
}
