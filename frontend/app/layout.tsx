import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SafeWander Next App',
  description: 'React/Next.js migration of SafeWander UI'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
