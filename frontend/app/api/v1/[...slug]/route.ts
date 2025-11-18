import { NextRequest, NextResponse } from 'next/server';

// Use BACKEND_API_URL (server-only, more secure) if available,
// otherwise fall back to NEXT_PUBLIC_API_URL (accessible client-side)
const BACKEND_URL = 
  process.env.BACKEND_API_URL || 
  process.env.NEXT_PUBLIC_API_URL || 
  'http://localhost:8000';

// Helper to forward headers (excluding hop-by-hop headers)
function getForwardHeaders(request: NextRequest): HeadersInit {
  const headers: HeadersInit = {};
  const skipHeaders = new Set([
    'host',
    'connection',
    'keep-alive',
    'transfer-encoding',
    'upgrade',
    'content-length', // Will be set by fetch automatically
  ]);

  request.headers.forEach((value, key) => {
    if (!skipHeaders.has(key.toLowerCase())) {
      headers[key] = value;
    }
  });

  return headers;
}

// Handle all HTTP methods
async function handler(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  try {
    // Build the backend URL
    const path = params.slug?.join('/') || '';
    const url = new URL(`${BACKEND_URL}/api/v1/${path}`);
    
    // Forward query parameters
    request.nextUrl.searchParams.forEach((value, key) => {
      url.searchParams.append(key, value);
    });

    // Prepare request options
    const requestOptions: RequestInit = {
      method: request.method,
      headers: getForwardHeaders(request),
    };

    // Forward body for methods that support it
    if (
      request.method !== 'GET' &&
      request.method !== 'HEAD' &&
      request.body
    ) {
      // Get the raw body as ArrayBuffer
      const body = await request.arrayBuffer();
      if (body.byteLength > 0) {
        requestOptions.body = body;
      }
    }

    console.log(`[Proxy] ${request.method} ${url.toString()}`);

    // Make the request to the backend
    const backendResponse = await fetch(url.toString(), requestOptions);

    // Get response body
    const responseBody = await backendResponse.arrayBuffer();

    // Forward the response
    return new NextResponse(responseBody, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: {
        // Forward relevant headers
        'Content-Type': backendResponse.headers.get('Content-Type') || 'application/json',
        'Cache-Control': backendResponse.headers.get('Cache-Control') || 'no-store',
        // Add CORS headers for client-side requests
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  } catch (error) {
    console.error('[Proxy] Error:', error);
    
    return NextResponse.json(
      {
        error: 'Backend connection failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        backend_url: BACKEND_URL,
      },
      { status: 502 }
    );
  }
}

// Export handlers for all HTTP methods
export async function GET(request: NextRequest, context: { params: { slug: string[] } }) {
  return handler(request, context);
}

export async function POST(request: NextRequest, context: { params: { slug: string[] } }) {
  return handler(request, context);
}

export async function PUT(request: NextRequest, context: { params: { slug: string[] } }) {
  return handler(request, context);
}

export async function DELETE(request: NextRequest, context: { params: { slug: string[] } }) {
  return handler(request, context);
}

export async function PATCH(request: NextRequest, context: { params: { slug: string[] } }) {
  return handler(request, context);
}

export async function OPTIONS(request: NextRequest, context: { params: { slug: string[] } }) {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
}

