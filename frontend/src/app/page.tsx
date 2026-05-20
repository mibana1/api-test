"use client";

import { FormEvent, useMemo, useState } from "react";
import type { Book } from "@/types/book";

type SearchMode = "unified" | "aladin" | "center" | "google" | "kakao" | "naver";

const API_BASE_URL = "http://127.0.0.1:8000";
const PAGE_SIZE = 12;

const SEARCH_ENDPOINTS: Record<SearchMode, string> = {
  unified: `${API_BASE_URL}/api/search/`,
  aladin: `${API_BASE_URL}/api/aladdin/search/`,
  center: `${API_BASE_URL}/api/center/search/`,
  google: `${API_BASE_URL}/api/google/search/`,
  kakao: `${API_BASE_URL}/api/kakao/search/`,
  naver: `${API_BASE_URL}/api/naver/search/`,
};

const SEARCH_LABELS: Record<SearchMode, string> = {
  unified: "All",
  aladin: "Aladin",
  center: "National Library",
  google: "Google Books",
  kakao: "Kakao",
  naver: "Naver",
};

function getBooks(payload: unknown): Book[] {
  if (Array.isArray(payload)) {
    return payload as Book[];
  }
  if (
    payload &&
    typeof payload === "object" &&
    "results" in payload &&
    Array.isArray((payload as { results: unknown }).results)
  ) {
    return (payload as { results: Book[] }).results;
  }
  return [];
}

function getVisiblePages(currentPage: number, pageCount: number) {
  if (pageCount <= 9) {
    return Array.from({ length: pageCount }, (_, index) => index + 1);
  }

  const pages = new Set([
    1,
    2,
    pageCount - 1,
    pageCount,
    currentPage - 1,
    currentPage,
    currentPage + 1,
  ]);
  const sortedPages = Array.from(pages)
    .filter((page) => page >= 1 && page <= pageCount)
    .sort((left, right) => left - right);

  return sortedPages.flatMap((page, index) => {
    const previous = sortedPages[index - 1];
    if (previous && page - previous > 1) {
      return [`ellipsis-${previous}-${page}`, page];
    }
    return [page];
  });
}

function nullableText(value: string | null | undefined) {
  return value && value.trim() ? value : "null";
}

function isTruncatedText(value: string | null | undefined) {
  return value ? /(?:\.{2,}|\u2026|\u22ef)\s*$/.test(value.trim()) : false;
}

function summaryText(value: string | null | undefined) {
  return isTruncatedText(value) ? "null" : nullableText(value);
}

function DetailValue({ label, value }: { label: string; value: string | null | undefined }) {
  if (label === "Link" && value && value.trim()) {
    return (
      <a href={value} target="_blank" rel="noreferrer" className="detailValueLink">
        {value}
      </a>
    );
  }

  return <>{nullableText(value)}</>;
}

function BookDetailModal({
  book,
  onClose,
}: {
  book: Book;
  onClose: () => void;
}) {
  const details: Array<[string, string | null | undefined]> = [
    ["Source", book.sources?.length ? book.sources.map((source) => SEARCH_LABELS[source]).join(", ") : SEARCH_LABELS[book.source]],
    ["Author", book.author],
    ["Publisher", book.publisher],
    ["Published", book.pubDate],
    ["ISBN", book.isbn],
    ["Cover", book.cover],
    ["Link", book.link],
  ];

  return (
    <div className="modalOverlay" role="presentation" onClick={onClose}>
      <section
        className="bookModal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="book-detail-title"
        onClick={(event) => event.stopPropagation()}
      >
        <button type="button" className="modalClose" onClick={onClose} aria-label="Close popup">
          x
        </button>
        <div className="modalCover">
          {book.cover ? (
            <img src={book.cover} alt={`${book.title} cover`} />
          ) : (
            <div className="coverPlaceholder">null</div>
          )}
        </div>
        <div className="modalBody">
          <p className="modalLabel">Book title</p>
          <h2 id="book-detail-title">{nullableText(book.title)}</h2>
          <p className="modalLabel">Summary</p>
          <p className="modalSummary">{summaryText(book.description)}</p>
          <dl className="detailList">
            {details.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>
                  <DetailValue label={label} value={value} />
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </section>
    </div>
  );
}

function BookCard({ book, onSelect }: { book: Book; onSelect: (book: Book) => void }) {
  const badges = book.sources?.length ? book.sources : [book.source];

  return (
    <article className="bookCard">
      <button type="button" className="coverFrame coverButton" onClick={() => onSelect(book)}>
        {book.cover ? (
          <img src={book.cover} alt={`${book.title} cover`} className="coverImage" />
        ) : (
          <div className="coverPlaceholder">No cover</div>
        )}
      </button>
      <div className="bookBody">
        <div className="badges">
          {badges.map((source) => (
            <span className={`badge badge-${source}`} key={`${book.id}-${source}`}>
              {SEARCH_LABELS[source]}
            </span>
          ))}
        </div>
        <h2>{book.title || "Untitled"}</h2>
        <p className="byline">{book.author || "Unknown author"}</p>
        <p className="meta">{book.publisher || "Unknown publisher"}</p>
        {book.pubDate ? <p className="date">{book.pubDate}</p> : null}
      </div>
    </article>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid" aria-label="Loading results">
      {Array.from({ length: 8 }).map((_, index) => (
        <div className="bookCard skeleton" key={index}>
          <div className="coverFrame skeletonBlock" />
          <div className="bookBody">
            <div className="skeletonLine short" />
            <div className="skeletonLine" />
            <div className="skeletonLine medium" />
            <div className="skeletonLine tiny" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<SearchMode>("unified");
  const [books, setBooks] = useState<Book[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const modes = useMemo(() => Object.keys(SEARCH_ENDPOINTS) as SearchMode[], []);
  const pageCount = Math.max(1, Math.ceil(books.length / PAGE_SIZE));
  const visiblePages = useMemo(
    () => getVisiblePages(currentPage, pageCount),
    [currentPage, pageCount],
  );
  const pagedBooks = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return books.slice(start, start + PAGE_SIZE);
  }, [books, currentPage]);
  const firstResult = books.length ? (currentPage - 1) * PAGE_SIZE + 1 : 0;
  const lastResult = Math.min(currentPage * PAGE_SIZE, books.length);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setError("Enter a search term.");
      setBooks([]);
      setCurrentPage(1);
      return;
    }

    setIsLoading(true);
    setError("");
    setHasSearched(true);
    setCurrentPage(1);
    setSelectedBook(null);

    try {
      const response = await fetch(SEARCH_ENDPOINTS[mode], {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: trimmedQuery }),
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? String((payload as { detail: unknown }).detail)
            : "Search request failed.";
        throw new Error(detail);
      }

      setBooks(getBooks(payload));
    } catch (caughtError) {
      setBooks([]);
      setCurrentPage(1);
      setError(caughtError instanceof Error ? caughtError.message : "Search failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <section className="searchBand">
        <div className="shell">
          <h1>Book Search</h1>
          <form className="searchForm" onSubmit={handleSubmit}>
            <div className="searchRow">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Title, author, keyword, ISBN"
                aria-label="Search books"
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? "Searching" : "Search"}
              </button>
            </div>
            <div className="sourceToggle" aria-label="Search source">
              {modes.map((sourceMode) => (
                <label key={sourceMode} className={mode === sourceMode ? "active" : ""}>
                  <input
                    type="radio"
                    name="source"
                    value={sourceMode}
                    checked={mode === sourceMode}
                    onChange={() => setMode(sourceMode)}
                  />
                  <span>{SEARCH_LABELS[sourceMode]}</span>
                </label>
              ))}
            </div>
          </form>
        </div>
      </section>

      <section className="resultsBand">
        <div className="shell">
          {error ? <div className="errorState">{error}</div> : null}
          {isLoading ? <SkeletonGrid /> : null}
          {!isLoading && books.length > 0 ? (
            <>
              <div className="resultsHeader">
                <p>
                  Showing {firstResult}-{lastResult} of {books.length} results
                </p>
              </div>
              <div className="grid">
                {pagedBooks.map((book) => (
                  <BookCard book={book} onSelect={setSelectedBook} key={book.id} />
                ))}
              </div>
              {pageCount > 1 ? (
                <nav className="pagination" aria-label="Search results pages">
                  <button
                    type="button"
                    onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                    disabled={currentPage === 1}
                    aria-label="Previous page"
                  >
                    &lt;
                  </button>
                  {visiblePages.map((page) => {
                    if (typeof page === "string") {
                      return (
                        <span className="paginationGap" aria-hidden="true" key={page}>
                          ...
                        </span>
                      );
                    }

                    return (
                      <button
                        type="button"
                        className={currentPage === page ? "active" : ""}
                        onClick={() => setCurrentPage(page)}
                        aria-current={currentPage === page ? "page" : undefined}
                        key={page}
                      >
                        {page}
                      </button>
                    );
                  })}
                  <button
                    type="button"
                    onClick={() => setCurrentPage((page) => Math.min(pageCount, page + 1))}
                    disabled={currentPage === pageCount}
                    aria-label="Next page"
                  >
                    &gt;
                  </button>
                </nav>
              ) : null}
            </>
          ) : null}
          {!isLoading && hasSearched && !error && books.length === 0 ? (
            <div className="emptyState">No results found.</div>
          ) : null}
        </div>
      </section>
      {selectedBook ? (
        <BookDetailModal book={selectedBook} onClose={() => setSelectedBook(null)} />
      ) : null}
    </main>
  );
}
