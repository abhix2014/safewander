export interface FeedPost {
  id: number;
  name: string;
  avatar: string;
  verified: boolean;
  location: string;
  text: string;
  image_emoji: string | null;
  likes: number;
  comments: number;
  is_safety_alert: boolean;
  created_at: string;
}

export interface FeedResponse {
  posts: FeedPost[];
}
