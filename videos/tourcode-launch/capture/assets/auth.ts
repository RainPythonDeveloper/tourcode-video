import { verifyPassword } from "./password"
import { startSession } from "./session"

export async function handleLogin(email: string, password: string) {
  const user = await findUser(email)
  if (user === undefined || !verifyPassword(password, user.passwordHash)) {
    return { ok: false, reason: "Wrong email or password" }
  }
  return { ok: true, session: startSession(user.id) }
}

async function findUser(email: string) {
  const users = [{ id: "u1", email: "a@b.c", passwordHash: "x1y2" }]
  return users.find((user) => user.email === email)
}
