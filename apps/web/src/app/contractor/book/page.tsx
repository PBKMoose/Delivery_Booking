import Link from "next/link";
import { BookingForm } from "./booking-form";

export default function BookPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-4 py-10">
      <header className="flex flex-col gap-1">
        <Link href="/" className="text-sm text-zinc-500 hover:underline">
          ← Home
        </Link>
        <h1 className="text-3xl font-semibold tracking-tight">Book a vehicle</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Booking as <strong>Demo Contractor Ltd</strong> (this will come from your
          login once accounts are added). New bookings wait for site approval.
        </p>
      </header>
      <BookingForm />
    </main>
  );
}
