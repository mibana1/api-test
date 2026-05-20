export type BookSource = "aladin" | "center" | "google" | "kakao" | "naver";

export type Book = {
  id: string;
  source: BookSource;
  sources: BookSource[];
  title: string;
  author: string;
  publisher: string;
  pubDate: string;
  cover: string | null;
  isbn: string | null;
  description: string | null;
  link: string | null;
};
