"use client";

import { useCallback, useEffect, useState } from "react";
import {
  api,
  formatDate,
  formatTime,
  ValidationError,
  type Booking,
  type BookingOptions,
  type DaySlots,
  type FieldErrors,
} from "@/lib/api";

const SITE_TZ_FALLBACK = "Europe/London";

/** Today's date as YYYY-MM-DD (what <input type="date"> uses). */
function todayIso(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

const inputClass =
  "w-full rounded-md border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900";

export function BookingForm() {
  // --- data loaded from the API ---
  const [options, setOptions] = useState<BookingOptions | null>(null);
  const [daySlots, setDaySlots] = useState<DaySlots | null>(null);
  const [bookings, setBookings] = useState<Booking[]>([]);

  // --- what the user has entered ---
  const [country, setCountry] = useState("GB");
  const [registration, setRegistration] = useState("");
  const [vehicleType, setVehicleType] = useState("");
  const [mgwKg, setMgwKg] = useState("");
  const [movementType, setMovementType] = useState("drop_off");
  const [day, setDay] = useState(todayIso);
  const [slotStart, setSlotStart] = useState<string | null>(null);

  // --- feedback ---
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<Booking | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const timeZone = daySlots?.timezone ?? SITE_TZ_FALLBACK;

  const refreshBookings = useCallback(() => {
    api.listBookings().then(setBookings).catch(() => setLoadError("Couldn't load bookings."));
  }, []);

  // Load dropdown options and existing bookings once, when the page opens.
  useEffect(() => {
    api.bookingOptions().then(setOptions).catch(() => setLoadError("Couldn't reach the API."));
    refreshBookings();
  }, [refreshBookings]);

  // Reload slots whenever the chosen day changes.
  useEffect(() => {
    if (!day) return;
    api.slots(day).then(setDaySlots).catch(() => setDaySlots(null));
  }, [day]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault(); // stop the browser doing a full-page form post
    setSubmitting(true);
    setErrors({});
    setCreated(null);
    try {
      const booking = await api.createBooking({
        registration_country: country,
        registration,
        vehicle_type: vehicleType,
        mgw_kg: mgwKg === "" ? "" : Number(mgwKg),
        movement_type: movementType,
        slot_start: slotStart,
      });
      setCreated(booking);
      setSlotStart(null);
      refreshBookings();
    } catch (err) {
      if (err instanceof ValidationError) setErrors(err.errors);
      else setErrors({ body: "Something went wrong. Please try again." });
    } finally {
      setSubmitting(false);
    }
  }

  if (loadError) {
    return <p className="rounded-md bg-red-50 p-4 text-red-800">{loadError}</p>;
  }
  if (!options) return <p>Loading…</p>;

  const mgwTonnes = mgwKg && !Number.isNaN(Number(mgwKg)) ? Number(mgwKg) / 1000 : null;

  return (
    <div className="flex flex-col gap-10">
      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-6">
        {/* ---------- Vehicle ---------- */}
        <fieldset className="flex flex-col gap-4">
          <legend className="mb-2 text-lg font-semibold">Vehicle</legend>

          <div className="grid gap-4 sm:grid-cols-[12rem_1fr]">
            <Field label="Country" error={errors.registration_country} htmlFor="country">
              <select
                id="country"
                className={inputClass}
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              >
                {options.countries.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Registration" error={errors.registration} htmlFor="registration">
              <input
                id="registration"
                className={`${inputClass} font-mono uppercase`}
                value={registration}
                onChange={(e) => setRegistration(e.target.value)}
                placeholder={country === "GB" ? "AB12 CDE" : ""}
                autoComplete="off"
              />
            </Field>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Vehicle type" error={errors.vehicle_type} htmlFor="vehicle-type">
              <select
                id="vehicle-type"
                className={inputClass}
                value={vehicleType}
                onChange={(e) => setVehicleType(e.target.value)}
              >
                <option value="">Select…</option>
                {options.vehicle_types.map((v) => (
                  <option key={v.value} value={v.value}>
                    {v.label}
                  </option>
                ))}
              </select>
            </Field>

            <Field
              label="Max gross weight (kg)"
              error={errors.mgw_kg}
              htmlFor="mgw"
              hint={
                mgwTonnes !== null
                  ? `= ${mgwTonnes.toLocaleString("en-GB")} tonnes`
                  : `${options.mgw_min_kg.toLocaleString()}–${options.mgw_max_kg.toLocaleString()} kg`
              }
            >
              <input
                id="mgw"
                type="number"
                inputMode="numeric"
                min={options.mgw_min_kg}
                max={options.mgw_max_kg}
                step={1}
                className={inputClass}
                value={mgwKg}
                onChange={(e) => setMgwKg(e.target.value)}
                placeholder="e.g. 3500"
              />
            </Field>
          </div>
        </fieldset>

        {/* ---------- Booking ---------- */}
        <fieldset className="flex flex-col gap-4">
          <legend className="mb-2 text-lg font-semibold">Booking</legend>

          <div className="flex gap-6">
            {options.movement_types.map((m) => (
              <label key={m.value} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="movement_type"
                  value={m.value}
                  checked={movementType === m.value}
                  onChange={() => setMovementType(m.value)}
                />
                {m.label}
              </label>
            ))}
          </div>
          {errors.movement_type && <ErrorText>{errors.movement_type}</ErrorText>}

          <Field label="Date" htmlFor="day">
            <input
              id="day"
              type="date"
              className={`${inputClass} sm:w-56`}
              value={day}
              min={todayIso()}
              onChange={(e) => {
                setDay(e.target.value);
                setSlotStart(null); // a slot from the old day no longer applies
              }}
            />
          </Field>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium">Arrival time slot ({timeZone})</span>
            {daySlots === null ? (
              <p className="text-sm text-zinc-500">Loading slots…</p>
            ) : (
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
                {daySlots.slots.map((slot) => {
                  const selected = slot.start === slotStart;
                  return (
                    <button
                      key={slot.start}
                      type="button"
                      disabled={!slot.available}
                      title={slot.reason ?? undefined}
                      onClick={() => setSlotStart(slot.start)}
                      aria-pressed={selected}
                      className={[
                        "rounded-md border px-2 py-2 text-sm tabular-nums",
                        selected
                          ? "border-blue-600 bg-blue-600 text-white"
                          : "border-zinc-300 hover:border-blue-500 dark:border-zinc-700",
                        "disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-zinc-300",
                      ].join(" ")}
                    >
                      {formatTime(slot.start, timeZone)}–{formatTime(slot.end, timeZone)}
                    </button>
                  );
                })}
              </div>
            )}
            {errors.slot_start && <ErrorText>{errors.slot_start}</ErrorText>}
          </div>
        </fieldset>

        {errors.body && <ErrorText>{errors.body}</ErrorText>}

        <button
          type="submit"
          disabled={submitting}
          className="self-start rounded-md bg-blue-600 px-5 py-2.5 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Booking…" : "Request booking"}
        </button>

        {created && (
          <p className="rounded-md border border-green-300 bg-green-50 p-4 text-green-900 dark:border-green-800 dark:bg-green-950 dark:text-green-100">
            Booking <strong className="font-mono">{created.reference}</strong> requested for{" "}
            {formatDate(created.slot_start, timeZone)} at {formatTime(created.slot_start, timeZone)}.
            It&apos;s pending approval by the site.
          </p>
        )}
      </form>

      {/* ---------- My bookings ---------- */}
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">My bookings</h2>
        {bookings.length === 0 ? (
          <p className="text-sm text-zinc-500">No bookings yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-300 text-zinc-500 dark:border-zinc-700">
                <tr>
                  <th className="py-2 pr-4">Ref</th>
                  <th className="py-2 pr-4">When</th>
                  <th className="py-2 pr-4">Vehicle</th>
                  <th className="py-2 pr-4">Type</th>
                  <th className="py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((b) => (
                  <tr key={b.id} className="border-b border-zinc-200 dark:border-zinc-800">
                    <td className="py-2 pr-4 font-mono">{b.reference}</td>
                    <td className="py-2 pr-4 whitespace-nowrap">
                      {formatDate(b.slot_start, timeZone)} {formatTime(b.slot_start, timeZone)}
                    </td>
                    <td className="py-2 pr-4 font-mono">
                      {b.vehicle.registration}{" "}
                      <span className="text-zinc-500">({b.vehicle.registration_country})</span>
                    </td>
                    <td className="py-2 pr-4">
                      {labelFor(options.vehicle_types, b.vehicle.vehicle_type)} ·{" "}
                      {labelFor(options.movement_types, b.movement_type)}
                    </td>
                    <td className="py-2 capitalize">{b.status.replace("_", " ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function labelFor(list: { value: string; label: string }[], value: string): string {
  return list.find((o) => o.value === value)?.label ?? value;
}

function Field({
  label,
  htmlFor,
  error,
  hint,
  children,
}: {
  label: string;
  htmlFor: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={htmlFor} className="text-sm font-medium">
        {label}
      </label>
      {children}
      {error ? (
        <ErrorText>{error}</ErrorText>
      ) : (
        hint && <span className="text-xs text-zinc-500">{hint}</span>
      )}
    </div>
  );
}

function ErrorText({ children }: { children: React.ReactNode }) {
  return (
    <span role="alert" className="text-sm text-red-600 dark:text-red-400">
      {children}
    </span>
  );
}
