import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Bourse Analytics',
  description: 'Real-time market analytics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <nav className="bg-primary text-white p-4 sticky top-0 z-50 shadow-md">
            <div className="container mx-auto flex justify-between items-center">
                <Link href="/" className="text-2xl font-bold tracking-tight">
                    Market<span className="text-accent">Data</span>
                </Link>
                <div className="space-x-4">
                    <Link href="/" className="hover:text-accent transition">Marché</Link>
                    <Link href="/companies" className="hover:text-accent transition">Sociétés</Link>
                    <Link href="/trading" className="hover:text-blue-400 transition">Trading</Link>
                    <Link href="/investment" className="hover:text-blue-400 transition">Investissement</Link>
                    <Link href="/predictions" className="hover:text-blue-400 transition">Prédictions</Link>
                </div>
            </div>
        </nav>
        <main className="container mx-auto p-4 min-h-screen">
            {children}
        </main>
        <footer className="bg-secondary text-slate-400 p-6 mt-8">
            <div className="container mx-auto text-center text-sm">
                &copy; {new Date().getFullYear()} Bourse Analytics. Données ClickHouse.
            </div>
        </footer>
      </body>
    </html>
  )
}
