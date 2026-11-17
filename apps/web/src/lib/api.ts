// Types and helpers for talking to the Python API.
// These mirror the Pydantic schemas in backend/app/schemas/booking.py.
// (Later we can generate this file automatically from the API's OpenAPI spec.)

export type Option = { value: string; label: string };

export type BookingOptions = {
  vehicle_types: Option[];
  movement_types: Option[];
  countries: Option[];
  mgw_min_kg: number;
  mgw_max_kg: number;
};

export type Slot = {
  start: string; // ISO date-time in UTC
  end: string;
  available: boolean;
  reason: string | null;
};

export type DaySlots = { timezone: string; slots: Slot[] };

export type BookingCreate = {
  registration_country: string;
  registration: string;
  vehicle_type: string;
  mgw_kg: number | string;
  movement_type: string;
  slot_start: string | null;
};

export type Booking = {
  id: number;
  reference: string;
  status: string;
  movement_type: string;
  slot_start: string;
  slot_end: string;
  created_at: string;
  vehicle: {
    registration: string;
    registration_country: string;
    vehicle_type: string;
    mgw_kg: number;
  };
};

/** Field name -> error message, as returned by the API on a 422. */
export type FieldErrors = Record<string, string>;

/** Thrown when the API rejects input; carries per-field messages for the form. */
export class ValidationError extends Error {
  constructor(public errors: FieldErrors) {
    super("Validation failed");
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (res.status === 422) {
    const body = (await res.json()) as { errors: FieldErrors };
    throw new ValidationError(body.errors);
  }
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as T;
}

export const api = {
  bookingOptions: () => request<BookingOptions>("/booking-options"),
  slots: (day: string) => request<DaySlots>(`/slots?day=${encodeURIComponent(day)}`),
  listBookings: () => request<Booking[]>("/bookings"),
  createBooking: (data: BookingCreate) =>
    request<Booking>("/bookings", { method: "POST", body: JSON.stringify(data) }),
};

/** Format an ISO time as e.g. "09:30" in the site's timezone. */
export function formatTime(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone,
  }).format(new Date(iso));
}

/** Format an ISO time as e.g. "Fri 20 Nov 2026" in the site's timezone. */
export function formatDate(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone,
  }).format(new Date(iso));
}
