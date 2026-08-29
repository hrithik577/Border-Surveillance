import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'IBVAP - Intelligent Border Video Analytics Platform',
  description: 'AI-Powered Border Surveillance & Threat Intelligence (SIH26-26187)',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-base text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
