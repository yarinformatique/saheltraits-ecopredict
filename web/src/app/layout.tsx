import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SahelTraits-DB & EcoPredict | Portail Web d'Aide à la Décision",
  description:
    "Portail web interactif d'aide à la décision et catalogue ouvert de traits multi-organes des espèces ligneuses sahéliennes. Modélisation bioclimatique CMIP6 2050–2080.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="h-full bg-slate-50">
      <body className="h-full flex flex-col antialiased selection:bg-emerald-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
