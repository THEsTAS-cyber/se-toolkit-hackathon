"use client";

import { useEffect, useState, useCallback } from "react";

export function useFavorites(token: string | null) {
  const [favIds, setFavIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!token) { setFavIds(new Set()); return; }
    fetch("/api/favorites", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.ok ? res.json() : [])
      .then((data) => setFavIds(new Set(data.map((g: { id: number }) => g.id))))
      .catch(() => {});
  }, [token]);

  const toggle = useCallback(async (gameId: number) => {
    if (!token) return;
    const isFav = favIds.has(gameId);
    const res = await fetch(`/api/favorites/${gameId}`, {
      method: isFav ? "DELETE" : "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok || res.status === 201 || res.status === 204) {
      setFavIds((prev) => {
        const next = new Set(prev);
        isFav ? next.delete(gameId) : next.add(gameId);
        return next;
      });
    }
  }, [token, favIds]);

  return { favIds, toggle };
}
