export function startSession(userId: string) {
  return { userId, startedAt: Date.now(), token: crypto.randomUUID() }
}
