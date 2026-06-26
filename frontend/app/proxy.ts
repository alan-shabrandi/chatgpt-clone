// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  // اگر از NextAuth استفاده می‌کنید، توکن را از کوکی بخوانید
  // اگر دستی مدیریت می‌کنید، باید وضعیت کوکیِ توکن را چک کنید
  const token =
    request.cookies.get("next-auth.session-token") ||
    request.cookies.get("token");

  const isAuthPage =
    request.nextUrl.pathname.startsWith("/login") ||
    request.nextUrl.pathname.startsWith("/register");

  // اگر کاربر توکن ندارد و می‌خواهد به صفحات محافظت شده برود
  if (!token && !isAuthPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // اگر کاربر لاگین است و می‌خواهد دوباره به صفحه لاگین/ثبت‌نام برود
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

// مسیرهایی که می‌خواهید این میدلور روی آن‌ها اعمال شود
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
