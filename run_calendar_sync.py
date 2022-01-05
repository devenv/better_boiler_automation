from ddtrace import tracer

from scheduler.calendar_sync import CalendarSync


def main():
    with tracer.trace("calendar sync"):
        CalendarSync().run()

if __name__ == "__main__":
    main()