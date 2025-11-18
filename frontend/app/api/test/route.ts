import { NextResponse } from 'next/server';

// Simple test endpoint to verify API routes are working on Vercel
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    message: 'API routes are working!',
    timestamp: new Date().toISOString(),
    env: {
      hasBackendUrl: !!process.env.BACKEND_API_URL,
      hasPublicUrl: !!process.env.NEXT_PUBLIC_API_URL,
      backendUrl: process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'not set'
    }
  });
}

