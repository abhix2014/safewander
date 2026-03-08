import type { FeedResponse } from '@/types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export async function fetchPosts(limit = 12): Promise<FeedResponse> {
  const res = await fetch(`${API_BASE}/api/v1/posts?limit=${limit}`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    throw new Error(`Unable to load posts (${res.status})`);
  }
  return (await res.json()) as FeedResponse;
}

export async function createPost(payload: {
  name: string;
  location: string;
  text: string;
}): Promise<{ ok: boolean; post_id: number }> {
  const res = await fetch(`${API_BASE}/api/v1/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const body = await res.json();
  if (!res.ok) {
    const message = body?.error ?? 'Unable to publish post';
    throw new Error(message);
  }
  return body as { ok: boolean; post_id: number };
}
