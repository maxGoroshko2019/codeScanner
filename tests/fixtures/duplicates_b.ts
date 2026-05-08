// File B with the same duplicated validation block

export function validateUserB(user: any): boolean {
  if (!user.name || user.name.length < 2) {
    return false;
  }
  if (!user.email || !user.email.includes('@')) {
    return false;
  }
  if (!user.age || user.age < 0 || user.age > 150) {
    return false;
  }
  return true;
}

export function otherStuffB(): void {
  console.log('unique code in file B');
}
