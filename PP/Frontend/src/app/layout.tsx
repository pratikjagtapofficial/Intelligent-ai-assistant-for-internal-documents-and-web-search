import type { Metadata } from "next";
import "./global.css";

export const metadata: Metadata = {
  title: "Company AI Assistant",
  description:
    "AI assistant for company policies and current web information",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}