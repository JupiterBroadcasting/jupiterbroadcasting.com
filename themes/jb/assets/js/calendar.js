const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

const updateSchedules = function(tzText) {
    const schedules = document.getElementsByClassName("schedule");
    const tzParts = tzText.match(
        "^\\(GMT(?<sign>[+-])(?<hours>[0-9]{2}):(?<minutes>[0-9]{2})\\) (?<name>[a-zA-Z ]+)( -|$)"
    );
    const tzSign = tzParts[1];
    const tzMinute = Number.parseInt(tzSign + tzParts[3], 10);

    // show data uses Pacific time, adjust by 8 hours
    const tzHour = Number.parseInt(tzSign + tzParts[2], 10) + 8;

    for (let x = 0; x < schedules.length; x++) {
        const type = schedules[x].getAttribute("data-live-schedule-type");
        let day = Number.parseInt(schedules[x].getAttribute("data-live-schedule-day"), 10);
        let hour = Number.parseInt(schedules[x].getAttribute("data-live-schedule-hour"), 10);
        let minute = Number.parseInt(schedules[x].getAttribute("data-live-schedule-minute") || "0", 10);

        minute += tzMinute;
        if (minute < 0) {
            hour -= 1;
            minute += 60;
        } else if (minute >= 60) {
            hour += 1;
            minute -= 60;
        }

        hour += tzHour;
        if (hour < 0) {
            day -= 1;
            hour += 24;
        } else if (hour >= 24) {
            day += 1;
            hour -= 24;
        }

        if (day < 0) {
            day += 7;
        } else if (day >= 7) {
            day -= 7;
        }

        let ampm = "am";
        if (hour >= 12) {
            ampm = "pm";
            if (hour > 12) {
                hour -= 12;
            }
        } else if (hour == 0) {
            hour = 12;
        }

        const tzName = tzParts[4];

        let scheduleHtml = "";
        if (type != "weekly") {
            scheduleHtml += "Alternating ";
        }
        const minuteText = minute.toString().padStart(2, '0');
        scheduleHtml += `${daysOfWeek[day]}s<br>${hour}:${minuteText}${ampm}&nbsp;${tzName}`;

        schedules[x].innerHTML = scheduleHtml;
    }
}

const calendarOnLoad = function() {
    const iframe = document.querySelector('iframe');
    const calendarBase = iframe.dataset.src;

    // Detect timezone automatically
    var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    var tzname = encodeURIComponent(tz);
    iframe.src = calendarBase + "&ctz=" + tzname;

    const ctz = document.querySelector('#ctz');
    ctz.value = tz;

    updateSchedules(ctz.options[ctz.selectedIndex].text);

    // Change on timezone after dropdown
    ctz.onchange = function () {
        var tzname = ctz.value;
        updateSchedules(ctz.options[ctz.selectedIndex].text)
        
        if(tzname && tzname != "none") {
            iframe.src = calendarBase + "&ctz=" + tzname;
        }
    };
}
