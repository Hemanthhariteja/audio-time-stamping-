'use client';

/**
 * Root layout component
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from '@/components/Layout';
import '@/styles/globals.css';

const queryClient = new QueryClient();

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>Audio Transcription Platform</title>
        <meta name="description" content="Professional audio transcription and analysis" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <Layout>{children}</Layout>
        </QueryClientProvider>
      </body>
    </html>
  );
}
