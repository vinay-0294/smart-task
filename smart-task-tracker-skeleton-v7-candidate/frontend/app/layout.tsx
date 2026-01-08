import './globals.css';

export const metadata = {
  title: 'Smart Task Tracker',
  description: 'A modern task management application with AI-powered intake',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          {children}
        </div>
      </body>
    </html>
  );
}
