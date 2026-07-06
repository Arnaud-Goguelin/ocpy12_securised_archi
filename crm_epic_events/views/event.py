from typing import TYPE_CHECKING

from crm_epic_events.utils.printers import print_error, print_info, print_option, print_success, print_title, prompt


if TYPE_CHECKING:
    from crm_epic_events.models import Event


class EventView:
    # --- Prompts ---

    @staticmethod
    def prompt_event_id() -> str:
        return prompt("Event ID").strip()

    @staticmethod
    def prompt_create() -> dict:
        print_title("Create new event")
        return {
            "contract_id": prompt("Contract ID").strip(),
            "customer_id": prompt("Customer ID").strip(),
            "start_date": prompt("Start date (YYYY-MM-DD HH:MM)").strip(),
            "end_date": prompt("End date (YYYY-MM-DD HH:MM)").strip(),
            "location": prompt("Location").strip(),
            "attendees": prompt("Number of attendees").strip(),
            "notes": prompt("Notes (optional)").strip() or None,
        }

    @staticmethod
    def prompt_update(target: "Event") -> dict:
        print_title(f"Update event — {target.id}")
        print_info("Leave blank to keep current value.")
        data = {}
        for field_name, current in [
            ("start_date", target.start_date.strftime("%Y-%m-%d %H:%M")),
            ("end_date", target.end_date.strftime("%Y-%m-%d %H:%M")),
            ("location", target.location),
            ("attendees", str(target.attendees)),
            ("notes", target.notes or ""),
            ("support_contact_id", str(target.support_contact_id) if target.support_contact_id else ""),
        ]:
            value = prompt(f"{field_name.replace('_', ' ').title()} (current: {current})").strip()
            if value:
                data[field_name] = value
        return data

    @staticmethod
    def prompt_select_event(events: list["Event"]) -> "Event | None":
        for i, event in enumerate(events, start=1):
            print_option(
                str(i),
                f"[{event.id}]  {event.location}  |  "
                f"{event.start_date.strftime('%Y-%m-%d')} → {event.end_date.strftime('%Y-%m-%d')}  |  "
                f"{event.attendees} attendees",
            )
        print_option("Q", "Cancel")
        raw = prompt("Select an event").strip().upper()
        if raw == "Q":
            return None
        try:
            return events[int(raw) - 1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid selection: '{raw}'") from None

    # --- Display ---

    @staticmethod
    def display_events(events: list["Event"], title: str = "Events") -> None:
        print_title(title)
        if not events:
            print_info("No events found.")
            return
        for event in events:
            support = str(event.support_contact_id) if event.support_contact_id else "— unassigned —"
            print_info(
                f"  [{event.id}]"
                f"  |  {event.location}"
                f"  |  {event.start_date.strftime('%Y-%m-%d %H:%M')} → {event.end_date.strftime('%Y-%m-%d %H:%M')}"
                f"  |  {event.attendees} attendees"
                f"  |  support: {support}"
            )

    @staticmethod
    def display_success(message: str) -> None:
        print_success(message)

    @staticmethod
    def display_error(message: str) -> None:
        print_error(message)
