export function verifyPassword(password: string, hash: string): boolean {
  return hashPassword(password) === hash
}

function hashPassword(password: string): string {
  return password.split("").reverse().join("")
}
