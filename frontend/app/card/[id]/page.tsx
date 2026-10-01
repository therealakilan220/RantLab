"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import ConceptCard from "@/components/ConceptCard";
import ShareActions from "@/components/ShareActions";
import { ApiRequestError, getCard } from "@/lib/api";
import { isSampleId } from "@/lib/samples";
import type { Card } from "@/lib/types";

export default function CardPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const [card, setCard] = useState<Card | null>(null);
  const [error, setError] = useState<string | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    getCard(id)
      .then((c) => {
        if (!cancelled) setCard(c);
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiRequestError && e.code === "not_found") setError("This plan doesn't exist or the link is wrong.");
        else setError(e instanceof ApiRequestError ? e.message : "Couldn't load this plan.");
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (error) {
    return (
      <div className="rounded-[28px] border border-line bg-surface p-10 text-center">
        <p className="font-display text-2xl font-bold text-ink">Plan not found</p>
        <p className="mt-2 text-ink-soft">{error}</p>
        <Link href="/" className="mt-6 inline-block rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">
          Start a new rant
        </Link>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="animate-pulse overflow-hidden rounded-[28px] border border-line bg-surface">
        <div className="h-44 bg-brand/80" />
        <div className="space-y-4 p-8">
          <div className="h-5 w-3/4 rounded-full bg-mist" />
          <div className="h-5 w-1/2 rounded-full bg-mist" />
          <div className="h-24 rounded-2xl bg-mist" />
          <div className="h-24 rounded-2xl bg-mist" />
        </div>
      </div>
    );
  }

  return (
    <div className="rise space-y-6">
      {isSampleId(card.id) && (
        <p className="text-sm text-ink-soft">
          Example plan, shown to illustrate what RantLab produces.
        </p>
      )}
      <div ref={cardRef}>
        <ConceptCard card={card} />
      </div>
      <ShareActions targetRef={cardRef} cardId={card.id} problem={card.problem} />
    </div>
  );
}