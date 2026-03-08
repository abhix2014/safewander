'use client';

import { useEffect, useState } from 'react';

import { createPost, fetchPosts } from '@/lib/api';
import type { FeedPost } from '@/types/api';

export function CommunityFeed() {
  const [posts, setPosts] = useState<FeedPost[]>([]);
  const [name, setName] = useState('Guest Traveler');
  const [location, setLocation] = useState('Rishikesh');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const data = await fetchPosts();
      setPosts(data.posts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load feed');
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function submitPost(e: React.FormEvent) {
    e.preventDefault();
    if (text.trim().length < 4) {
      setError('Write at least 4 characters');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await createPost({ name: name.trim(), location: location.trim(), text: text.trim() });
      setText('');
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to publish post');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-4 text-xs uppercase tracking-wider text-saffron">Community</div>
      <h2 className="text-3xl font-bold">Live Traveler Feed</h2>
      <p className="mt-3 text-sm text-white/65">Powered by the same backend APIs, now consumed by React components.</p>

      <form onSubmit={submitPost} className="sw-card mt-6 grid gap-3 p-4">
        <textarea
          className="min-h-24 rounded-md border border-white/10 bg-black/20 p-3 text-sm text-white outline-none"
          placeholder="Share a trip tip, buddy request, or safety alert..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="grid gap-2 md:grid-cols-[1fr_180px_auto]">
          <input
            className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
          />
          <input
            className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm text-white outline-none"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Location"
          />
          <button disabled={loading} className="rounded-md bg-saffron px-4 py-2 text-sm font-bold text-[#1A0F00] disabled:opacity-70">
            {loading ? 'Posting...' : 'Post'}
          </button>
        </div>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
      </form>

      <div className="mt-5 grid gap-3">
        {posts.map((post) => (
          <article key={post.id} className={`sw-card p-4 ${post.is_safety_alert ? 'border-red-400/40' : ''}`}>
            <div className="mb-2 flex items-center gap-2 text-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-saffron font-bold text-[#1A0F00]">{post.avatar}</div>
              <div>
                <div className="font-semibold">{post.name}</div>
                <div className="text-xs text-white/60">📍 {post.location}</div>
              </div>
            </div>
            <p className={`text-sm leading-6 ${post.is_safety_alert ? 'text-red-200' : 'text-white/80'}`}>{post.text}</p>
            <div className="mt-3 flex gap-4 text-xs text-white/50">
              <span>🤍 {post.likes}</span>
              <span>💬 {post.comments}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
