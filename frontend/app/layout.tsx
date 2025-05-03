// app/layout.tsx
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Анализатор кода",
  // Здесь определяем фавиконки — Next.js сам подставит нужные теги <link>
  icons: {
    icon: [
      { url: "https://static.beeline.ru/upload/dpcupload/contents/342/avatarbee_2704.svg", sizes: "any", type: "image/x-icon" }
    ],
    shortcut: [{ url: "/bazya-m.png" }],
    apple: [{ url: "/bazya-m.png" }]
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
