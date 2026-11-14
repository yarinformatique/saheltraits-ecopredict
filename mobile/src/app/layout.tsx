import type { Metadata, Viewport } from 'next';
import './globals.css';
import Navigation from '@/components/Navigation';
import OfflineBadge from '@/components/OfflineBadge';

export const metadata: Metadata = {
  title: 'SahelField — Collecte Mobile & Enquêtes (Doctorat 2026-2029)',
  description: 'Application mobile terrain offline-first pour inventaires dendrométriques, traits fonctionnels et enquêtes socio-écologiques.',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'SahelField',
  },
};

export const viewport: Viewport = {
  themeColor: '#1e4125',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col antialiased selection:bg-emerald-600 selection:text-white pb-20">
        {/* Offline & Network Status Header */}
        <header className="sticky top-0 z-30 shadow-md">
          <OfflineBadge />
        </header>

        {/* Main Content Area */}
        <main className="flex-1 max-w-lg w-full mx-auto p-4 sm:p-5">
          {children}
        </main>

        {/* Mobile App Bottom Navigation */}
        <Navigation />

        {/* PWA Service Worker Registration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').then(
                    function(registration) {
                      console.log('SahelField ServiceWorker enregistré avec succès:', registration.scope);
                    },
                    function(err) {
                      console.log('Erreur enregistrement ServiceWorker:', err);
                    }
                  );
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
