import Link from "next/link";
import { ApiStatus } from "./api-status";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-16">
      <h1 className="text-3xl font-semibold tracking-tight">Delivery Booking</h1>
      <p className="text-zinc-600 dark:text-zinc-400">
        Development build. Admin, contractor and gate portals will appear here as
        they are built.
      </p>
      <ApiStatus />
      <Link
        href="/contractor/book"
        className="self-start rounded-md bg-blue-600 px-5 py-2.5 font-medium text-white hover:bg-blue-700"
      >
        Book a vehicle →
      </Link>
    </main>
  );
}
