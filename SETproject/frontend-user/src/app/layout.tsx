import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "./AuthProvider";
import AuthNav from "./AuthNav";
import NanobotWidget from "@/components/NanobotWidget";

export const metadata: Metadata = {
  title: "ProjectSET — PS Store Prices",
  description: "Compare game prices across 67 PS Store regions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <header className="header">
            <nav className="nav-content">
              <div className="nav-left">
                <a href="/games" className="nav-logo">🎮 PS Prices</a>
              </div>
              <div className="nav-links">
                <a href="/games" className="nav-link">Catalog</a>
                <a href="/favorites" className="nav-link">Wishlist</a>
              </div>
              <div className="nav-right">
                <AuthNav />
              </div>
            </nav>
          </header>
          <main>{children}</main>
          <NanobotWidget />
        </AuthProvider>
      </body>
    </html>
  );
}
